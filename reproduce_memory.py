
from backend.app.agents.agent import Agent, Soul
from backend.app.env.world import World
import numpy as np

def test_social_memory():
    world = World(100, 100)
    
    # 1. Setup: Alice and Bob start close
    a1 = Agent(x=50, y=50, name="Alice", gender="female")
    a2 = Agent(x=50, y=55, name="Bob", gender="male") # Dist 5
    
    world.add_agent(a1)
    world.add_agent(a2)
    
    # 2. Force Scan (They see each other)
    print("--- Step 1: Initial Contact ---")
    a1.scan_surroundings(world)
    
    # Verify memory
    mem = a1.spatial_memory.get('agent', [])
    print(f"Alice Memory Count: {len(mem)}")
    if mem:
        print(f"Alice remembers: {mem[0]}")
    
    # 3. Teleport Bob away (Simulate him running away)
    print("\n--- Step 2: Bob Vanishes ---")
    a2.prev_x, a2.prev_y = a2.x, a2.y
    a2.x, a2.y = 90, 90 # Far away
    
    # 4. Alice acts (Should seek memory)
    # Force Desire to Socialize
    a1.qalb.social = 0.0 
    
    print(f"Alice at {a1.x},{a1.y}. Bob at {a2.x},{a2.y}")
    
    a1.act(2, world)
    
    # Check logs
    print(f"Alice Action Plan Executed.")
    
    # Verify movement direction
    # Initial memory was 50,55. Alice is at 50,50. Should move +y (0, 1) or random if memory fail.
    # Momentum initializes 0,0.
    
    if a1.y > 50:
        print(f"SUCCESS: Alice moved Towards Memory (New Y: {a1.y})")
    else:
         print(f"FAILURE: Alice moved Randomly/Stayed (New Y: {a1.y})")
         
    # Check if memory persists
    a1.scan_surroundings(world) # Should NOT wipe memory
    mem_after = a1.spatial_memory.get('agent', [])
    print(f"Alice Memory Count After Scan: {len(mem_after)}")

if __name__ == "__main__":
    test_social_memory()
