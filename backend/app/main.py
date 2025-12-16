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
    # Enforce 50/50 split for initial population
    gender = "male" if i % 2 == 0 else "female"
    agent = Agent(x=np.random.randint(0, 50), y=np.random.randint(0, 50), gender=gender)
    
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
    # world.evolve_generation()
    return {"message": "Evolution is continuous. Agents reproduce biologically.", "generation": world.generation}

@app.post("/speed")
def set_speed(speed: float):
    global SIMULATION_SPEED
    SIMULATION_SPEED = max(0.0001, min(2.0, speed))
    return {"message": "Speed updated", "speed": SIMULATION_SPEED}

# --- JSON Encoder for Numpy ---
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super(NumpyEncoder, self).default(obj)

def sanitize_for_json(obj):
    """
    Recursively replace NaN and Infinity with None to ensure valid JSON.
    """
    if isinstance(obj, float):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return obj
    elif isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(v) for v in obj]
    elif isinstance(obj, np.floating):
         if np.isnan(obj) or np.isinf(obj):
            return None
         return float(obj)
    elif isinstance(obj, np.integer): # Handle numpy ints here too for safety
        return int(obj)
    elif isinstance(obj, np.ndarray):
        return sanitize_for_json(obj.tolist())
    return obj

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
        print("WS: Starting loop")
        while True:
            paused = getattr(world, 'paused', False)
            if not paused:
                # Decouple Simulation Loop from Rendering
                # If speed is very fast (low SIMULATION_SPEED), run multiple steps per frame
                steps_per_frame = 1
                if SIMULATION_SPEED < 0.005: steps_per_frame = 20
                elif SIMULATION_SPEED < 0.01: steps_per_frame = 10
                elif SIMULATION_SPEED < 0.05: steps_per_frame = 5
                
                try:
                    for _ in range(steps_per_frame):
                        # Run one simulation step
                        # Agents
                        agents = list(world.agents.values())
                        for agent in agents:
                            if agent.id not in world.agents: continue # Died during this step
                            try:
                                agent.act(world.time_step, world)
                            except TypeError as e:
                                 # Fallback if signature mismatch during dev
                                 print(f"WS: Error in agent.act: {e}")
                                 agent.act(np.random.randint(0,6), world)
                            except Exception as e:
                                print(f"WS: Critical error in agent.act: {e}")
                        
                        # Animals
                        for animal in world.animals:
                            animal.act(world)
                        
                        # Respawn Resources
                        world.respawn_resources()
                        
                        world.time_step += 1
                except Exception as e:
                    print(f"WS: Error in Simulation Step: {e}")
            
            # Send state to frontend (only once per frame)
            try:
                state = world.get_state()
                state["paused"] = paused
                
                # OPTIMIZATION: Only sanitize dynamic entities where NaNs occur.
                # Sanitizing the entire terrain (200x200) is too slow and unnecessary (ints).
                state["agents"] = sanitize_for_json(state["agents"])
                state["animals"] = sanitize_for_json(state["animals"])
                
                await websocket.send_text(json.dumps(state, cls=NumpyEncoder))
            except RuntimeError as e:
                # Catch "Cannot call 'send' once a close message has been sent"
                if "close message" in str(e):
                    print("WS: Connection closed during send.")
                    break
                else:
                    print(f"WS: RuntimeError sending state: {e}")
                    import traceback
                    traceback.print_exc()
            except Exception as e:
                print(f"WS: Error sending state: {e}")
                import traceback
                traceback.print_exc()
                # Retry or break?
                await asyncio.sleep(1)
            
            # Control simulation speed
            # If fast forwarding, minimum sleep to yield to event loop
            sleep_time = SIMULATION_SPEED if SIMULATION_SPEED >= 0.01 else 0.01
            await asyncio.sleep(sleep_time) 
    except WebSocketDisconnect:
        print("Client disconnected")
        receive_task.cancel()
    except Exception as e:
        print(f"WS: Fatal Error in loop: {e}")
        receive_task.cancel()

# Wrap with Socket.IO (Must be done after all routes are defined)
app = socketio.ASGIApp(sio, app)

if __name__ == "__main__":
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
