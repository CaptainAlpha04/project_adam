from app.env.test_world import TestWorld
import time
import threading
import sys

def input_thread(world):
    print("Commands: 'q' to quit, 'i' to inspect random agent, 's' to stats")
    while True:
        cmd = input()
        if cmd == 'q':
            print("Quitting...")
            os._exit(0)
        elif cmd == 'i':
            import random
            if world.agents:
                agent = random.choice(list(world.agents.values()))
                print(f"\n--- Agent Inspection ---")
                print(f"Name: {agent.attributes.name}")
                print(f"Life: #{agent.past_lives}")
                print(f"Age: {agent.get_age(world.time_tick)}")
                print(f"Hunger: {agent.needs.hunger:.2f}")
                print(f"Memories: {len(agent.memory)}")
                if agent.memory:
                    print(f"Last Memory: {agent.memory[-1].description}")
                print("------------------------\n")
        elif cmd == 's':
            print(f"\nStats: Tick {world.time_tick}, Agents {len(world.agents)}")

if __name__ == "__main__":
    import os
    try:
        world = TestWorld(num_agents=50)
        print("Starting Test World Simulation...")
        
        # Start input thread
        t = threading.Thread(target=input_thread, args=(world,))
        t.daemon = True
        t.start()
        
        epoch = 0
        while True:
            epoch += 1
            world.run_epoch(steps=100) # Smaller steps for more responsiveness
            # time.sleep(0.1) # Slight delay to allow reading logs
            
    except KeyboardInterrupt:
        print("\nSimulation Stopped.")
