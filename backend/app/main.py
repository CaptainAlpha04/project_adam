from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import json
import numpy as np
from .env.world import World
from .agents.agent import Agent
from .env.animals import Animal

app = FastAPI(title="Project Adam Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize World
world = World(width=200, height=200)

# Add some initial agents
for i in range(10):
    agent = Agent(x=np.random.randint(0, 200), y=np.random.randint(0, 200))
    world.add_agent(agent)

# Add animals
for i in range(200):
    # Herbivores
    h = Animal(x=np.random.randint(0, 200), y=np.random.randint(0, 200), type='herbivore')
    world.animals.append(h)
    
for i in range(10):
    # Carnivores
    c = Animal(x=np.random.randint(0, 200), y=np.random.randint(0, 200), type='carnivore')
    world.animals.append(c)

@app.get("/")
def read_root():
    return {"message": "Project Adam Backend is running", "agent_count": len(world.agents), "animal_count": len(world.animals)}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Task to handle incoming commands (Pause)
    async def receive_commands():
        try:
            while True:
                data = await websocket.receive_text()
                try:
                    command = json.loads(data)
                    if command.get("type") == "pause":
                        world.paused = not getattr(world, 'paused', False)
                except json.JSONDecodeError:
                    pass
        except Exception:
            pass # Disconnect handled in main loop

    receive_task = asyncio.create_task(receive_commands())

    try:
        while True:
            if not getattr(world, 'paused', False):
                # Run one simulation step
                # Agents
                # Create a list of values to avoid runtime error if dict changes size during iteration (death)
                agents = list(world.agents.values())
                for agent in agents:
                    if agent.id not in world.agents: continue # Died during this step
                    action = np.random.randint(0, 6)
                    agent.act(action, world)
                
                # Animals
                for animal in world.animals:
                    animal.act(world)
                
                # Respawn Resources
                world.respawn_resources()
                
                world.time_step += 1
            
            # Send state to frontend
            state = world.get_state()
            state["paused"] = getattr(world, 'paused', False)
            await websocket.send_text(json.dumps(state))
            
            # Control simulation speed
            await asyncio.sleep(0.1) 
    except WebSocketDisconnect:
        print("Client disconnected")
        receive_task.cancel()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
