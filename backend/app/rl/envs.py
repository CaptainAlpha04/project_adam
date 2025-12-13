import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Optional
from ..env.test_world import TestWorld
from ..agents.agent import Agent

class AdamBaseEnv(gym.Env):
    """
    Base Gym Environment for Adam Agents.
    Observation: Local Grid (Vision) + Internal State (Hunger, Health)
    Action: Discrete (Move, Interact, Craft)
    """
    metadata = {"render_modes": ["human", "ascii"], "render_fps": 4}

    def __init__(self, render_mode=None, width=20, height=20):
        self.width = width
        self.height = height
        self.render_mode = render_mode
        
        # Action Space: 
        # 0: Stay, 1: Up, 2: Down, 3: Left, 4: Right, 5: Eat/Interact
        self.action_space = spaces.Discrete(6)
        
        # Observation Space:
        # Vision: 5x5 grid around agent. Each cell has 3 channels (Entity Type, ID, Property)
        # Internal: Hunger (0-1), Health (0-1)
        # Flattened for simplicity initially: 5*5*3 + 2 = 77
        self.observation_space = spaces.Box(low=0, high=1, shape=(77,), dtype=np.float32)
        
        self.world = TestWorld(width=width, height=height, num_agents=0) # Managed manually
        self.agent: Optional[Agent] = None

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        # Reset World
        self.world = TestWorld(width=self.width, height=self.height, num_agents=0)
        
        # Spawn Agent
        self.world.spawn_agent()
        self.agent = list(self.world.agents.values())[0]
        
        # Spawn Food (Scenario specific, but base needs some)
        for _ in range(5):
            fx, fy = np.random.randint(0, self.width), np.random.randint(0, self.height)
            self.world.food_grid.add((fx, fy))
            
        return self._get_obs(), {}

    def step(self, action):
        # Decode Action
        dx, dy = 0, 0
        if action == 1: dy = -1
        elif action == 2: dy = 1
        elif action == 3: dx = -1
        elif action == 4: dx = 1
        
        # Execute Move
        if action in [1, 2, 3, 4]:
            self.world.move_agent(self.agent.id, dx, dy)
            
        # Execute Interact (Eat)
        reward = -0.01 # Time penalty (Entropy)
        terminated = False
        truncated = False
        
        if action == 5:
            if (self.agent.x, self.agent.y) in self.world.food_grid:
                self.world.food_grid.remove((self.agent.x, self.agent.y))
                self.agent.state.hunger = max(0, self.agent.state.hunger - 0.5)
                reward += 10.0 # Big reward for eating
                # Respawn food to keep episode going
                fx, fy = np.random.randint(0, self.width), np.random.randint(0, self.height)
                self.world.food_grid.add((fx, fy))
        
        # Update State
        self.agent.state.hunger += 0.005
        
        # Check Death
        if self.agent.state.hunger >= 1.0:
            reward -= 10.0 # Death penalty
            terminated = True
            
        # Max steps truncation handled by wrapper usually, but can add here
        
        return self._get_obs(), reward, terminated, truncated, {}

    def _get_obs(self):
        # Construct 5x5 grid observation
        # For now, simplified: Just relative vector to nearest food + internal state
        
        # Find nearest food
        nearest_dist = float('inf')
        fx, fy = 0, 0
        for (fdx, fdy) in self.world.food_grid:
            dist = abs(fdx - self.agent.x) + abs(fdy - self.agent.y)
            if dist < nearest_dist:
                nearest_dist = dist
                fx, fy = fdx, fdy
        
        # Normalize relative position
        rel_x = (fx - self.agent.x) / self.width
        rel_y = (fy - self.agent.y) / self.height
        
        # Placeholder for full grid
        obs = np.zeros(77, dtype=np.float32)
        obs[0] = rel_x
        obs[1] = rel_y
        obs[2] = self.agent.state.hunger
        
        return obs

    def render(self):
        if self.render_mode == "ascii":
            grid = [['.' for _ in range(self.width)] for _ in range(self.height)]
            
            for (fx, fy) in self.world.food_grid:
                grid[fy][fx] = 'F'
                
            grid[self.agent.y][self.agent.x] = 'A'
            
            print("-" * (self.width + 2))
            for row in grid:
                print("|" + "".join(row) + "|")
            print("-" * (self.width + 2))
            print(f"Hunger: {self.agent.state.hunger:.2f}")

class MovementEnv(AdamBaseEnv):
    """
    Scenario: Learn to move towards food.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class CraftingEnv(AdamBaseEnv):
    """
    Scenario: Learn to gather resources and craft.
    """
    def reset(self, seed=None, options=None):
        obs, info = super().reset(seed=seed)
        # Spawn Trees and Rocks
        self.world.items_grid = {} # Clear items
        for _ in range(10):
            tx, ty = np.random.randint(0, self.width), np.random.randint(0, self.height)
            self.world.items_grid[(tx, ty)] = {'type': 'tree', 'amount': 10}
            
            rx, ry = np.random.randint(0, self.width), np.random.randint(0, self.height)
            self.world.items_grid[(rx, ry)] = {'type': 'rock', 'amount': 10}
        return obs, info

    def step(self, action):
        # Action 5 is Interact (Gather/Craft)
        obs, reward, terminated, truncated, info = super().step(action)
        
import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Optional
from ..env.test_world import TestWorld
from ..agents.agent import Agent

class AdamBaseEnv(gym.Env):
    """
    Base Gym Environment for Adam Agents.
    Observation: Local Grid (Vision) + Internal State (Hunger, Health)
    Action: Discrete (Move, Interact, Craft)
    """
    metadata = {"render_modes": ["human", "ascii"], "render_fps": 4}

    def __init__(self, render_mode=None, width=20, height=20):
        self.width = width
        self.height = height
        self.render_mode = render_mode
        
        # Action Space: 
        # 0: Stay, 1: Up, 2: Down, 3: Left, 4: Right, 5: Eat/Interact
        self.action_space = spaces.Discrete(6)
        
        # Observation Space:
        # Vision: 5x5 grid around agent. Each cell has 3 channels (Entity Type, ID, Property)
        # Internal: Hunger (0-1), Health (0-1)
        # Flattened for simplicity initially: 5*5*3 + 2 = 77
        self.observation_space = spaces.Box(low=0, high=1, shape=(77,), dtype=np.float32)
        
        self.world = TestWorld(width=width, height=height, num_agents=0) # Managed manually
        self.agent: Optional[Agent] = None

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        # Reset World
        self.world = TestWorld(width=self.width, height=self.height, num_agents=0)
        
        # Spawn Agent
        self.world.spawn_agent()
        self.agent = list(self.world.agents.values())[0]
        
        # Spawn Food (Scenario specific, but base needs some)
        for _ in range(5):
            fx, fy = np.random.randint(0, self.width), np.random.randint(0, self.height)
            self.world.food_grid.add((fx, fy))
            
        return self._get_obs(), {}

    def step(self, action):
        # Decode Action
        dx, dy = 0, 0
        if action == 1: dy = -1
        elif action == 2: dy = 1
        elif action == 3: dx = -1
        elif action == 4: dx = 1
        
        # Execute Move
        if action in [1, 2, 3, 4]:
            self.world.move_agent(self.agent.id, dx, dy)
            
        # Execute Interact (Eat)
        reward = -0.01 # Time penalty (Entropy)
        terminated = False
        truncated = False
        
        if action == 5:
            if (self.agent.x, self.agent.y) in self.world.food_grid:
                self.world.food_grid.remove((self.agent.x, self.agent.y))
                self.agent.state.hunger = max(0, self.agent.state.hunger - 0.5)
                reward += 10.0 # Big reward for eating
                # Respawn food to keep episode going
                fx, fy = np.random.randint(0, self.width), np.random.randint(0, self.height)
                self.world.food_grid.add((fx, fy))
        
        # Update State
        self.agent.state.hunger += 0.005
        
        # Check Death
        if self.agent.state.hunger >= 1.0:
            reward -= 10.0 # Death penalty
            terminated = True
            
        # Max steps truncation handled by wrapper usually, but can add here
        
        return self._get_obs(), reward, terminated, truncated, {}

    def _get_obs(self):
        # Delegate to Agent
        if self.agent:
            return self.agent.get_observation(self.world)
        return np.zeros(77, dtype=np.float32)

    def render(self):
        if self.render_mode == "ascii":
            grid = [['.' for _ in range(self.width)] for _ in range(self.height)]
            
            for (fx, fy) in self.world.food_grid:
                grid[fy][fx] = 'F'
                
            grid[self.agent.y][self.agent.x] = 'A'
            
            print("-" * (self.width + 2))
            for row in grid:
                print("|" + "".join(row) + "|")
            print("-" * (self.width + 2))
            print(f"Hunger: {self.agent.state.hunger:.2f}")

class MovementEnv(AdamBaseEnv):
    """
    Scenario: Learn to move towards food.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class CraftingEnv(AdamBaseEnv):
    """
    Scenario: Learn to gather resources and craft.
    """
    def reset(self, seed=None, options=None):
        obs, info = super().reset(seed=seed)
        
        # Track discovered recipes this episode
        self.discovered_recipes = set()
        
        # Clear items
        self.world.items_grid = {} 
        
        # Dense Spawning: Spawn resources IMMEDIATELY around the agent
        # Agent is at self.agent.x, self.agent.y
        # Spawn in a 5x5 area around agent
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if dx == 0 and dy == 0: continue # Don't spawn on top of agent initially
                
                tx = (self.agent.x + dx) % self.width
                ty = (self.agent.y + dy) % self.height
                
                # 50% chance to spawn something
                if np.random.random() < 0.5:
                    is_tree = np.random.random() < 0.5
                    if is_tree:
                        self.world.items_grid[(tx, ty)] = {'type': 'tree', 'amount': 5}
                    else:
                        self.world.items_grid[(tx, ty)] = {'type': 'rock', 'amount': 5}

        return obs, info

    def step(self, action):
        # Action 5 is Interact (Gather/Craft)
        obs, reward, terminated, truncated, info = super().step(action)
        
        if action == 5:
            # 1. Gather Resource (if on top)
            pos = (self.agent.x, self.agent.y)
            gathered = False
            if pos in self.world.items_grid:
                item = self.world.items_grid[pos]
                if item['type'] == 'tree':
                    self.agent.add_resource('wood', 1)
                    reward += 1.0 
                    gathered = True
                elif item['type'] == 'rock':
                    self.agent.add_resource('stone', 1)
                    reward += 1.0
                    gathered = True
            
            # 2. Crafting (if not gathering, or even if gathering, try to craft)
            # Check for valid recipes
            # We need RECIPES from agent.py
            from ..agents.agent import RECIPES
            
            # Simple Inventory Dict
            inv = {}
            for slot in self.agent.inventory:
                name = slot['item']['name'].lower()
                inv[name] = inv.get(name, 0) + slot['count']
            
            crafted_something = False
            for recipe_name, ingredients in RECIPES.items():
                can_craft = True
                for mat, count in ingredients.items():
                    if inv.get(mat.lower(), 0) < count:
                        can_craft = False
                        break
                
                if can_craft:
                    # Craft it!
                    for mat, count in ingredients.items():
                        self.agent.add_resource(mat.lower(), -count)
                        
                    self.agent.add_resource(recipe_name, 1)
                    crafted_something = True
                    
                    # Reward Logic
                    if recipe_name not in self.discovered_recipes:
                        self.discovered_recipes.add(recipe_name)
                        reward += 100.0 # Huge reward for NEW discovery
                        # print(f"*** DISCOVERED NEW RECIPE: {recipe_name} ***")
                    else:
                        reward += 10.0 # Smaller reward for repeat crafting
                    
                    # Only craft one thing per step to avoid instant depletion
                    break 
            
            if not gathered and not crafted_something:
                reward -= 0.1 # Penalty for useless clicking
                
        return obs, reward, terminated, truncated, info

class SocialEnv(AdamBaseEnv):
    """
    Scenario: Learn to interact with other agents.
    """
    def reset(self, seed=None, options=None):
        obs, info = super().reset(seed=seed)
        # Spawn other agents (NPCs)
        for _ in range(3):
            self.world.spawn_agent()
        return obs, info
        
    def step(self, action):
        obs, reward, terminated, truncated, info = super().step(action)
        
        # Reward for being near other agents
        agents = list(self.world.agents.values())
        if len(agents) > 1:
            min_dist = float('inf')
            for other in agents:
                if other.id == self.agent.id: continue
                dist = abs(other.x - self.agent.x) + abs(other.y - self.agent.y)
                if dist < min_dist: min_dist = dist
            
            if min_dist < 3:
                reward += 0.1 # Proximity reward
                
        return obs, reward, terminated, truncated, info
