
import sys
import os
import numpy as np

# Add backend to path
sys.path.append(os.getcwd())

from app.env.world import World
from app.agents.agent import Agent, AgentNeeds
from app.env.item import Item

def test_humanity():
    print("Initializing World...")
    world = World(100, 100)
    
    # Create Agent
    alice = Agent(10, 10, name="Alice")
    alice.attributes.personality_vector["Greed"] = 0.1 # Not Greedy
    alice.attributes.personality_vector["Social"] = 0.5
    alice.attributes.personality_vector["Aggression"] = 0.0
    world.add_agent(alice)
    
    print("\n--- Testing Metacognition ---")
    alice.reflect(world)
    print(f"Daily Focus: {alice.daily_focus}")
    print(f"Life Goal: {alice.life_goal}")
    if alice.daily_focus in ["Work", "Social", "Rest", "Exploration"]:
        print("PASS: Daily focus set.")
    else:
        print("FAIL: Daily focus invalid.")

    print("\n--- Testing Nerfed Gathering ---")
    # Alice is NOT greedy. Should she pick up random wood?
    # Context: Not Hungry, Focus Random.
    # Force Focus to 'Rest' to ensure she ignores work
    alice.daily_focus = "Rest"
    wood = Item("wood", "Wood", weight=1.0, hardness=1.0, durability=1.0, tags=["material"])
    world._add_item(10, 10, wood)
    
    # Act
    alice.act(0, world)
    
    # Check inventory
    if alice.get_resource_count("Wood") == 0:
        print("PASS: Alice ignored wood while resting (Human behavior).")
    else:
        print("FAIL: Alice picked up wood like a robot.")
        
    print("\n--- Testing Trade (Gifting vs Barter) ---")
    bob = Agent(11, 11, name="Bob")
    # Make Bob Hungry
    bob.needs.hunger = 0.8
    
    # Alice has food
    food = Item("apple", "Apple", weight=0.1, hardness=0.1, durability=0.1, tags=["food", "consumable"])
    alice.inventory.append({'item': food.to_dict(), 'count': 5})
    
    # 1. Friends -> Gift
    print("Scenario 1: Friends")
    alice.opinions[bob.id] = 0.8 # High opinion
    alice.communicate(bob, world) # Should trigger trade (Gift)
    
    if bob.get_resource_count("Apple") > 0:
        print("PASS: Alice gifted apple to friend Bob.")
    else:
        print("FAIL: Alice did not gift.")
        
    # Reset
    alice.inventory = []
    bob.inventory = []
    alice.inventory.append({'item': food.to_dict(), 'count': 5})
    bob.add_resource("Wood", 5, tags=["material"])
    
    # 2. Strangers -> Barter
    print("Scenario 2: Strangers (Barter)")
    alice.opinions[bob.id] = 0.0 # Stranger
    alice.life_goal = "Builder" # She wants wood
    alice.needs.hunger = 0.0
    
    # Bob is still hungry (Needs food), Has Wood (Surplus)
    bob.needs.hunger = 0.8
    
    # Alice initiates
    # She has Surplus Food (5 > 3), Needs Wood
    alice.communicate(bob, world)
    
    # Check Swap
    # Alice should have +1 Wood, -1 Apple
    # Bob should have +1 Apple, -1 Wood
    
    if alice.get_resource_count("Wood") > 0:
         print("PASS: Barter successful! Alice got Wood.")
    else:
         print("FAIL: Barter failed.")

    print("Audit Complete.")

if __name__ == "__main__":
    test_humanity()
