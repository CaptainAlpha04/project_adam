import os

content = r'''import time
import numpy as np
from typing import Dict, List, Optional, Set, Tuple
from ..agents.agent import Agent, Soul

class TestWorld:
    def __init__(self, width=100, height=100, num_agents=10):
        self.width = width
        self.height = height
        self.agents: Dict[str, Agent] = {}
        self.time_tick = 0
        self.dead_souls: List[Soul] = []
        self.food_grid: Set[Tuple[int, int]] = set()
        self.animals = [] 
        self.items_grid = {} 
        
        # print(f"Initializing TestWorld with {num_agents} agents...")
        for _ in range(num_agents):
            self.spawn_agent()

    def spawn_agent(self, soul: Soul = None):
        x = np.random.randint(0, self.width)
        y = np.random.randint(0, self.height)
        agent = Agent(x, y, soul=soul, birth_time=self.time_tick)
        self.agents[agent.id] = agent
        if soul:
            print(f"[SAMSARA] Agent {agent.attributes.name} reborn! Life #{agent.past_lives}. Memories: {len(agent.memory)}")

    def move_agent(self, agent_id, dx, dy):
        agent = self.agents.get(agent_id)
        if not agent: return False
        
        nx, ny = agent.x + dx, agent.y + dy
        if 0 <= nx < self.width and 0 <= ny < self.height:
            agent.x = nx
            agent.y = ny
            return True
        return False
        
    def log_event(self, msg):
        pass

    def run_epoch(self, steps=1000):
        start_time = time.time()
        deaths_this_epoch = 0
        
        for i in range(steps):
            deaths = self.step()
            deaths_this_epoch += deaths
            
        elapsed = time.time() - start_time
        fps = steps / elapsed if elapsed > 0 else 0
        print(f"Epoch: {steps} steps | Time: {elapsed:.2f}s | Speed: {fps:.2f} iter/s | Deaths: {deaths_this_epoch} | Pop: {len(self.agents)}")

    def step(self):
        self.time_tick += 1
        deaths = 0
        
        # Spawn Food (Randomly)
        if len(self.food_grid) < 50: # Maintain some food
            fx, fy = np.random.randint(0, self.width), np.random.randint(0, self.height)
            self.food_grid.add((fx, fy))
        
        agent_ids = list(self.agents.keys())
        for aid in agent_ids:
            agent = self.agents.get(aid)
            if not agent: continue
            
            # Entropy Ticker
            agent.state.hunger += 0.005 
            
            # Act
            agent.act(0, self)
            
            # Eat Food?
            if (agent.x, agent.y) in self.food_grid:
                self.food_grid.remove((agent.x, agent.y))
                agent.state.hunger = max(0, agent.state.hunger - 0.3)
                agent.add_memory(f"Ate food at {agent.x},{agent.y}", type="survival", impact=0.5)
                # print(f"Agent {agent.attributes.name} ate food!")
            
            # Check Death
            if agent.state.hunger >= 1.0:
                self.handle_death(agent, "starvation")
                deaths += 1
                
        while self.dead_souls:
            soul = self.dead_souls.pop(0)
            self.spawn_agent(soul)
            
        return deaths

    def handle_death(self, agent, cause):
        # Record death memory
        agent.add_memory(f"Died of {cause}", type="death", impact=-1.0)
        
        soul = agent.create_soul()
        self.dead_souls.append(soul)
        if agent.id in self.agents:
            del self.agents[agent.id]
        
        if agent.past_lives > 0 or len(agent.memory) > 0:
             # print(f"[DEATH] Agent {agent.attributes.name} (Life {agent.past_lives}) died of {cause}. Soul preserved.")
             pass
'''

with open('backend/app/env/test_world.py', 'w') as f:
    f.write(content)
print("Updated backend/app/env/test_world.py silently")
