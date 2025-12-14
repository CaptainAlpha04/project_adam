
from backend.app.agents.agent import Agent, Soul
from backend.app.env.world import World
import numpy as np

def test_social_interaction():
    world = World(100, 100)
    
    # Create two agents face to face
    # Override random spawn? The Agent init takes x,y but World.add_agent overrides it?
    # Checking world.add_agent... yes, it respawns them in a circle!
    # checking world.py:171...
    # We must manually place them AFTER adding to world or modify add_agent usage in test.
    # Or just set their positions manually after add.
    
    a1 = Agent(x=0, y=0, name="Alice", gender="female")
    a2 = Agent(x=0, y=0, name="Bob", gender="male")
    
    world.add_agent(a1)
    world.add_agent(a2)
    
    # FORCE PROXIMITY
    a1.x, a1.y = 50, 50
    a2.x, a2.y = 50, 56 # Dist 6
    
    # FORCE CURIOSITY/SOCIAL DESIRE
    # Make them lonely
    a1.qalb.social = 0.0
    a1.qalb.fun = 0.0
    
    # Ensure they see each other (determinism fix should handle this if < 20)
    
    print(f"Start: A1 at {a1.x},{a1.y} | A2 at {a2.x},{a2.y} | Dist: {a1.distance_to(a2)}")
    
    # A1 act
    a1.act(1, world)
    
    print(f"Step 1: A1 Action Plan Executed.")
    print(f"        A1 Lock: {a1.state.social_lock_target}")
    
    if a1.state.social_lock_target == a2.id:
        print("SUCCESS: Social Lock Engaged!")
    else:
        print("FAILURE: No Social Lock.")
        
    print("A1 Diary:", a1.diary)

if __name__ == "__main__":
    test_social_interaction()
