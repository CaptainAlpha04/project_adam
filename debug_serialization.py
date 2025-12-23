import json
import numpy as np
import sys
import os

# Add parent directory to path to import app modules
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend.app.env.world import World
from backend.app.agents.agent import Agent

# Mock NumpyEncoder
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating) or isinstance(obj, float):
            if np.isnan(obj) or np.isinf(obj):
                return None # Valid JSON null
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super(NumpyEncoder, self).default(obj)

def sanitize_for_json(obj):
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
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.ndarray):
        return sanitize_for_json(obj.tolist())
    return obj

def test_serialization():
    print("Initializing World...")
    world = World(width=50, height=50)
    
    # Add dummy agents with complex relations
    a1 = Agent(x=10, y=10, gender='male')
    a2 = Agent(x=12, y=12, gender='female')
    world.add_agent(a1)
    world.add_agent(a2)
    
    # Form tribe
    world.spawn_child(a1, a2)
    
    # Run simulation steps...
    print("Running simulation steps...")
    for i in range(100):
        # INJECT FAILURE
        if i == 50:
            print("Injecting NaN into agent state...")
            list(world.agents.values())[0].nafs.hunger = float('nan')

        # Simulate act
        for agent in list(world.agents.values()):
            try:
                agent.act(world.time_step, world)
            except Exception as e:
                pass # Ignore act errors, focusing on serialization
        world.time_step += 1
        
        # Test Serialization
        try:
            state = world.get_state()
            
            # OPTIMIZATION: Match backend logic
            state["agents"] = sanitize_for_json(state["agents"])
            state["animals"] = sanitize_for_json(state["animals"])
            
            json_str = json.dumps(state, cls=NumpyEncoder)
            if "NaN" in json_str or "Infinity" in json_str:
                print(f"CRITICAL: NaN or Infinity detected in JSON at Step {i}")
                # Print snippet
                idx = json_str.find("NaN")
                if idx == -1: idx = json_str.find("Infinity")
                print(json_str[max(0, idx-50):min(len(json_str), idx+50)])
                return

            if i % 10 == 0:
                print(f"Step {i}: Serialization OK (Length: {len(json_str)})")
        except Exception as e:
            print(f"CRITICAL SERIALIZATION ERROR at Step {i}: {e}")
            import traceback
            traceback.print_exc()
            return

    print("Test Complete. No critical serialization errors found.")

if __name__ == "__main__":
    test_serialization()
