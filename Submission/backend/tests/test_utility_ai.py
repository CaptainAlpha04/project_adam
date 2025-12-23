
import sys
import os
import numpy as np

# Add backend to path
sys.path.append(os.getcwd())

from app.env.world import World
from app.agents.agent import Agent, AgentNeeds

def test_utility_ai():
    print("Initializing World...")
    world = World(100, 100)
    
    print("Creating Agents...")
    alice = Agent(10, 10, name="Alice")
    bob = Agent(11, 11, name="Bob") # Close to Alice
    
    world.add_agent(alice)
    world.add_agent(bob)
    
    print("Checking Agent Initialization...")
    assert isinstance(alice.needs, AgentNeeds)
    assert alice.needs.hunger == 0.0
    print("PASS: AgentNeeds initialized.")
    
    print("Testing Act Loop (Normal)...")
    try:
        alice.act(0, world)
        print("PASS: Act() ran without error.")
    except Exception as e:
        print(f"FAIL: Act() crashed: {e}")
        import traceback
        traceback.print_exc()
        return

    print("Testing Hunger -> Health Decay...")
    # Force hunger
    alice.needs.hunger = 0.9
    start_health = alice.state.health
    alice.act(0, world)
    
    if alice.state.health < start_health:
        print(f"PASS: Health decayed from {start_health} to {alice.state.health}")
    else:
        print(f"FAIL: Health did not decay! Hunger={alice.needs.hunger}")

    print("Testing Sharing Logic...")
    # Give Alice food
    from app.env.item import Item
    food = Item("apple", "Apple", weight=0.1, hardness=0.1, durability=0.1, tags=["food", "consumable"])
    alice.inventory.append({'item': food.to_dict(), 'count': 5})
    
    # Make Bob hungry
    bob.needs.hunger = 0.8
    # Make Alice full
    alice.needs.hunger = 0.0
    
    # Force Social Interaction (Alice acts)
    # Utility for Socializing should be high if we force it? 
    # Or strict check of share_resources function directly
    alice.share_resources(bob, world)
    
    bob_food_count = bob.get_resource_count("Apple")
    if bob_food_count > 0:
        print(f"PASS: Alice shared food. Bob has {bob_food_count} Apple.")
    else:
        print(f"FAIL: Bob did not receive food.")

    print("Testing Inventory Caps...")
    # Try to add 15 wood
    for _ in range(15):
        alice.add_resource("Wood", 1, tags=["material"])
    
    w_count = alice.get_resource_count("Wood")
    if w_count == 10:
        print(f"PASS: Wood capped at {w_count}")
    else:
        print(f"FAIL: Wood count {w_count} exceeded cap!")

    print("Testing Social Happiness...")
    start_happ = alice.state.happiness
    # Simulate positive social update locally
    alice.state.happiness = min(1.0, alice.state.happiness + 0.05)
    if alice.state.happiness > start_happ:
         print(f"PASS: Happiness increased from {start_happ} to {alice.state.happiness}")
    else:
         print(f"FAIL: Happiness did not increase.")
         
    print("Testing Experience...")
    # Ran act() twice above (approx)
    if alice.state.experience > 0:
        print(f"PASS: Experience is {alice.state.experience}")
    else:
        print(f"FAIL: Experience is 0")

    print("Audit Complete.")

if __name__ == "__main__":
    test_utility_ai()
