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

# Global Simulation Speed (seconds per tick)
SIMULATION_SPEED = 0.1

# Initialize World
world = World(width=200, height=200)

# Add some initial agents
for i in range(10):
    agent = Agent(x=np.random.randint(0, 50), y=np.random.randint(0, 50))
    world.add_agent(agent)

# Add animals
for i in range(20):
    # Herbivores
    h = Animal(x=np.random.randint(0, 50), y=np.random.randint(0, 50), type='herbivore')
    world.animals.append(h)
    
for i in range(5):
    # Carnivores
    c = Animal(x=np.random.randint(0, 50), y=np.random.randint(0, 50), type='carnivore')
    world.animals.append(c)

@app.get("/")
def read_root():
    return {
        "message": "Project Adam Backend is running", 
        "agent_count": len(world.agents), 
        "animal_count": len(world.animals), 
        "generation": world.generation,
        "speed": SIMULATION_SPEED
    }

@app.post("/evolve")
def evolve_world():
    world.evolve_generation()
    return {"message": "Evolution triggered", "generation": world.generation}

@app.post("/speed")
def set_speed(speed: float):
    global SIMULATION_SPEED
    SIMULATION_SPEED = max(0.01, min(2.0, speed))
    return {"message": "Speed updated", "speed": SIMULATION_SPEED}

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
            paused = getattr(world, 'paused', False)
            if not paused:
                # Run one simulation step
                # Agents
                agents = list(world.agents.values())
                for agent in agents:
                    if agent.id not in world.agents: continue # Died during this step
                    # agent.act(world.time_step, world) # Old signature?
                    # Check signature of act
                    try:
                        agent.act(world.time_step, world)
                    except TypeError:
                         # Fallback if signature mismatch during dev
                         agent.act(np.random.randint(0,6), world)
                
                # Animals
                for animal in world.animals:
                    animal.act(world)
                
                # Respawn Resources
                world.respawn_resources()
                
                world.time_step += 1
            
            # Send state to frontend
            state = world.get_state()
            state["paused"] = paused
            await websocket.send_text(json.dumps(state))
            
            # Control simulation speed
            await asyncio.sleep(SIMULATION_SPEED) 
    except WebSocketDisconnect:
        print("Client disconnected")
        receive_task.cancel()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
