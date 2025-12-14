
from backend.app.agents.agent import Agent, Soul, GameStrategy
from backend.app.env.world import World
import numpy as np

def test_game_theory():
    world = World(100, 100)
    
    # 1. Setup: Alice (Altruist -> Always Cooperate) vs Bob (Aggressive -> Always Defect)
    a1 = Agent(x=50, y=50, name="Alice", gender="female")
    a1.attributes.personality_vector["Altruism"] = 0.9
    a1.attributes.personality_vector["Aggression"] = 0.1
    a1.determine_strategy()
    
    a2 = Agent(x=50, y=55, name="Bob", gender="male")
    a2.attributes.personality_vector["Altruism"] = 0.1
    a2.attributes.personality_vector["Aggression"] = 0.9
    a2.determine_strategy()
    
    world.add_agent(a1)
    world.add_agent(a2)
    
    print(f"Alice Strategy: {a1.attributes.strategy}")
    print(f"Bob Strategy: {a2.attributes.strategy}")
    
    # Force social lock
    a1.state.social_lock_target = a2.id
    a1.state.social_lock_steps = 3
    
    a2.state.social_lock_target = a1.id
    # We must ensure Bob also "plays" if Alice calls him, OR simulating Bob's move is enough.
    # In my impl, Alice calls `target.make_game_decision`.
    
    print("\n--- Round 1 ---")
    a1.process_social_loop(world)
    
    # Expected: Alice Coops, Bob Defects.
    # Alice Opinion of Bob should DROP.
    print(f"Alice Opinion of Bob: {a1.qalb.opinions.get(a2.id)}")
    print(f"Alice Social Memory of Bob: {a1.qalb.social_memory.get(a2.id)}")
    print(f"Alice Diary: {a1.diary[-1]}")
    
    if a1.qalb.social_memory.get(a2.id) == 'defect':
        print("SUCCESS: Alice remembers Bob defected.")
    else:
        print("FAILURE: Alice did not record defection.")

if __name__ == "__main__":
    test_game_theory()
