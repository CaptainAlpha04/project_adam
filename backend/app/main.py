from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import json
import numpy as np
import socketio
from .env.world import World
from .agents.agent import Agent
from .env.animals import Animal
from .api.training import router as training_router
from .rl.training_manager import sio

app = FastAPI(title="Project Adam Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Training Router
app.include_router(training_router)

# Global Simulation Speed (seconds per tick)
SIMULATION_SPEED = 0.1

# Initialize World
world = World(width=200, height=200)

# Add some initial agents
for i in range(10):
    agent = Agent(x=np.random.randint(0, 50), y=np.random.randint(0, 50))
    
    # Try to load a brain (movement default)
    import os
    if os.path.exists("adam_soul_movement.zip"):
        agent.load_brain("adam_soul_movement")
    elif os.path.exists("adam_soul.zip"):
         agent.load_brain("adam_soul")
         
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

# Note: WebSocket endpoint for main simulation remains, but Socket.IO handles training updates.

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
    SIMULATION_SPEED = max(0.0001, min(2.0, speed))
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
                # Decouple Simulation Loop from Rendering
                # If speed is very fast (low SIMULATION_SPEED), run multiple steps per frame
                steps_per_frame = 1
                if SIMULATION_SPEED < 0.005: steps_per_frame = 20
                elif SIMULATION_SPEED < 0.01: steps_per_frame = 10
                elif SIMULATION_SPEED < 0.05: steps_per_frame = 5
                
                for _ in range(steps_per_frame):
                    # Run one simulation step
                    # Agents
                    agents = list(world.agents.values())
                    for agent in agents:
                        if agent.id not in world.agents: continue # Died during this step
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
            
            # Send state to frontend (only once per frame)
            state = world.get_state()
            state["paused"] = paused
            await websocket.send_text(json.dumps(state))
            
            # Control simulation speed
            # If fast forwarding, minimum sleep to yield to event loop
            sleep_time = SIMULATION_SPEED if SIMULATION_SPEED >= 0.01 else 0.01
            await asyncio.sleep(sleep_time) 
    except WebSocketDisconnect:
        print("Client disconnected")
        receive_task.cancel()

# Wrap with Socket.IO (Must be done after all routes are defined)
app = socketio.ASGIApp(sio, app)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
