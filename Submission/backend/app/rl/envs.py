import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Optional, Dict, Any
from ..agents.agent import Agent
# Note: We assume TestWorld is available, or we might need to Mock it if backend is not running.
# For training, we usually want a lightweight World. If TestWorld is heavy, we might need a distinct TrainingWorld.
from ..env.test_world import TestWorld 

class SamsaraEnv(gym.Env):
    """
    The Samsara Environment.
    A standardized Gym interface for Project Adam agents to learn via Curriculum Learning.
    
    Phases:
    1. SURVIVAL: Learn to move and eat. (Reward: Alive, Hunger reduction)
    2. GATHERING: Learn to collect resources. (Reward: Inventory inc)
    3. SOCIETY: Learn to interact. (Reward: Social inc)
    """
    metadata = {"render_modes": ["human", "ascii", "rgb_array"], "render_fps": 30}

    def __init__(self, render_mode=None, width=40, height=40, phase="SURVIVAL"):
        super(SamsaraEnv, self).__init__()
        self.render_mode = render_mode
        self.width = width
        self.height = height
        self.phase = phase
        
        # --- ACTION SPACE ---
        # 0: Wait
        # 1: Up, 2: Down, 3: Left, 4: Right
        # 5: Interact (Eat/Gather/Talk based on context)
        # 6: Craft/Special (Contextual)
        self.action_space = spaces.Discrete(7)
        
        # --- OBSERVATION SPACE ---
        # We use a Dict space for structured learning (CNN for vision, MLP for stats)
        
        # Vision Grid: 7x7 View
        # C0: Terrain/Walls (0: Empty, 1: Wall/Water)
        # C1: Food (0: None, 1: Food)
        # C2: Resource (0: None, 1: Tree, 2: Rock)
        # C3: Agents (0: None, 1: Neutral, 2: Friend, 3: Enemy)
        self.vision_range = 3 # 3 radius = 7x7 grid
        grid_size = (self.vision_range * 2) + 1
        
        self.observation_space = spaces.Dict({
            "vision": spaces.Box(low=0, high=3, shape=(4, grid_size, grid_size), dtype=np.uint8),
            "internal": spaces.Box(low=0, high=1, shape=(5,), dtype=np.float32) 
            # [Hunger, Energy, Health, Social, InventoryCount]
        })
        
        self.world = TestWorld(width=width, height=height, num_agents=0)
        self.agent: Optional[Agent] = None
        self.step_count = 0
        self.max_steps = 1000

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        # 1. Reset World Structure
        self.world = TestWorld(width=self.width, height=self.height, num_agents=0)
        self.step_count = 0
        
        # 2. Spawn Hero Agent
        self.world.spawn_agent()
        self.agent = list(self.world.agents.values())[0]
        
        # 3. Setup Scenario based on Phase
        self._setup_scenario()
        
        return self._get_obs(), {}

    def _setup_scenario(self):
        """Populates the world based on the current Curriculum Phase."""
        # PHASE 1: SURVIVAL
        # Lots of food, no predators, simple terrain
        if self.phase == "SURVIVAL":
            # Spawn Food Randomly
            for _ in range(20):
                fx, fy = np.random.randint(1, self.width-1), np.random.randint(1, self.height-1)
                self.world.food_grid.add((fx, fy))
                
        # PHASE 2: GATHERING (To be implemented)
        elif self.phase == "GATHERING":
            from ..env.item import Item
            import uuid
            # Spawn Trees/Rocks
            for _ in range(20):
                fx, fy = np.random.randint(1, self.width-1), np.random.randint(1, self.height-1)
                val = np.random.random()
                if val < 0.5:
                    # Create Tree (Wood) Item
                    wood = Item(id=f"tree_{uuid.uuid4()}", name="Wood", weight=2.0, hardness=1.0, durability=5.0, tags=["material", "wood"])
                    self.world.items_grid[(fx, fy)] = [wood] # List of Items
                else:
                    # Create Rock (Stone) Item
                    stone = Item(id=f"rock_{uuid.uuid4()}", name="Stone", weight=5.0, hardness=3.0, durability=10.0, tags=["material", "stone"])
                    self.world.items_grid[(fx, fy)] = [stone] # List of Items
                    
        # PHASE 3: SOCIETY (To be implemented)
        elif self.phase == "SOCIETY":
            # Spawn random agents
            for _ in range(5):
                self.world.spawn_agent()

    def step(self, action):
        self.step_count += 1
        
        # 1. Decode Action (RL -> Game Logic)
        move_dir = (0, 0)
        should_interact = False
        
        if action == 1: move_dir = (0, -1) # Up
        elif action == 2: move_dir = (0, 1) # Down
        elif action == 3: move_dir = (-1, 0) # Left
        elif action == 4: move_dir = (1, 0) # Right
        elif action == 5: should_interact = True
        
        # 2. Apply Physics
        if move_dir != (0, 0):
            # Check bounds/walls (Simplified collision)
            tx = self.agent.x + move_dir[0]
            ty = self.agent.y + move_dir[1]
            if 0 <= tx < self.width and 0 <= ty < self.height:
                 self.agent.x, self.agent.y = tx, ty
                 
        if should_interact:
            # Try Eat
            if (self.agent.x, self.agent.y) in self.world.food_grid:
                self.world.food_grid.remove((self.agent.x, self.agent.y))
                self.agent.nafs.hunger = max(0.0, self.agent.nafs.hunger - 0.4)
                # Respawn food to ensure continuous training
                fx, fy = np.random.randint(1, self.width-1), np.random.randint(1, self.height-1)
                self.world.food_grid.add((fx, fy))
        
        # 3. Update Internal Systems (Biological Decay)
        # We manually tick the Nafs system to simulate time passing
        self.agent.nafs.update(self.world)
        
        # 4. Calculate Reward
        reward = self._calculate_reward()
        
        # 5. Check Termination
        terminated = False
        if self.agent.state.health <= 0:
            terminated = True
            reward -= 10.0 # Death penalty
            
        truncated = self.step_count >= self.max_steps
        
        return self._get_obs(), reward, terminated, truncated, {}

def compute_samsara_observation(agent, world, vision_range=3):
    """
    Standalone function to compute the observation for a given agent.
    Used by both the Training Env and the Live Inference Loop.
    """
    grid_size = (vision_range * 2) + 1 # 7
    width = world.width
    height = world.height
    vision = np.zeros((4, grid_size, grid_size), dtype=np.uint8)
    
    cx, cy = agent.x, agent.y
    
    for dy in range(-vision_range, vision_range + 1):
        for dx in range(-vision_range, vision_range + 1):
            # Grid Coordinates (0 to 6)
            gx, gy = dx + vision_range, dy + vision_range
            # World Coordinates
            wx, wy = cx + dx, cy + dy
            
            # Check Bounds
            if not (0 <= wx < width and 0 <= wy < height):
                vision[0, gy, gx] = 1 # Wall/OOB
                continue
            
            # Check Bounds
            if not (0 <= wx < width and 0 <= wy < height):
                vision[0, gy, gx] = 1 # Wall/OOB
                continue
            
            # Check Items at (wx, wy)
            if (wx, wy) in world.items_grid:
                items = world.items_grid[(wx, wy)]
                if items:
                    first_item = items[0]
                    
                    # Channel 1: Food
                    if "food" in first_item.tags or "Fruit" in first_item.name:
                        vision[1, gy, gx] = 1
                        
                    # Channel 2: Resources (Wood/Stone)
                    # Determine type from name or tags
                    if "Wood" in first_item.name:
                        vision[2, gy, gx] = 1 # Tree/Wood
                    elif "Stone" in first_item.name:
                        vision[2, gy, gx] = 2 # Rock/Stone
                
            # Channel 3: Agents (Not self)
            # This is O(N), for training usually fine. For inference, optimize if needed.
            # Using world.agents dict iteration might be slow if 100s of agents.
            # But grid is small (7x7). Better to iterate spatial map if available?
            # Current World doesn't have a spatial agent map. Iterate all.
            for other in world.agents.values():
                if other.id == agent.id: continue
                if other.x == wx and other.y == wy:
                        vision[3, gy, gx] = 1 # Neutral (TODO: Friendship color)

    # Internal State
    # [Hunger, Energy, Health, Social, InventoryCount]
    internal = np.array([
        agent.nafs.hunger,
        agent.nafs.energy,
        agent.state.health,
        agent.qalb.social,
        len(agent.inventory) / 20.0 # Normalized
    ], dtype=np.float32)
    
    return {
        "vision": vision,
        "internal": internal
    }

class SamsaraEnv(gym.Env):
    # ... (existing class methods) ...
    
    def _get_obs(self):
        return compute_samsara_observation(self.agent, self.world, self.vision_range)

    def _calculate_reward(self):
        """
        Curriculum-based Reward Function.
        """
        reward = 0.0
        
        # PHASE 1: ALIVE & FULL
        if self.phase == "SURVIVAL":
            # Survival Bonus
            reward += 0.01 
            
            # Full Belly Bonus (Encourage eating)
            if self.agent.nafs.hunger < 0.2:
                reward += 0.05
            elif self.agent.nafs.hunger > 0.8:
                reward -= 0.05
                
        elif self.phase == "SOCIETY":
            # Survival Baseline
            reward += 0.01
            
            # Social Proximity Reward
            agents = list(self.world.agents.values())
            min_dist = float('inf') # Initialize to safe default
            
            if len(agents) > 1:
                for other in agents:
                    if other.id == self.agent.id: continue
                    dist = abs(other.x - self.agent.x) + abs(other.y - self.agent.y)
                    if dist < min_dist: min_dist = dist
                
                # Reward for being close (Tribe building)
                if min_dist < 4:
                    reward += 0.1
                elif min_dist < 8:
                    reward += 0.05
                    
                # GAME THEORY: Passive Personality Interaction
                # If very close, personalities interact automatically
                if min_dist < 2.0:
                    # Simple Prisoner's Dilemma based on Traits
                    # My traits
                    my_agreeable = self.agent.attributes.personality_vector.get("Altruism", 0.5)
                    my_aggro = self.agent.attributes.personality_vector.get("Aggression", 0.5)
                    
                    # Decide Strategy: Cooperate if Nice > Aggro
                    my_strat = "COOPERATE" if my_agreeable > my_aggro else "DEFECT"
                    
                    # Other's traits (Simplified: Random or based on their actual traits if available)
                    # We pick the nearest agent for this interaction
                    nearest = None
                    for other in agents: # Re-find nearest
                         if other.id != self.agent.id:
                             dist = abs(other.x - self.agent.x) + abs(other.y - self.agent.y)
                             if dist == min_dist:
                                 nearest = other
                                 break
                    
                    if nearest:
                        other_agreeable = nearest.attributes.personality_vector.get("Altruism", 0.5)
                        other_aggro = nearest.attributes.personality_vector.get("Aggression", 0.5)
                        other_strat = "COOPERATE" if other_agreeable > other_aggro else "DEFECT"
                        
                        # Payoff Matrix (Standard PD)
                        if my_strat == "COOPERATE" and other_strat == "COOPERATE":
                            reward += 0.2 # Both win
                        elif my_strat == "COOPERATE" and other_strat == "DEFECT":
                            reward -= 0.5 # Sucker
                        elif my_strat == "DEFECT" and other_strat == "COOPERATE":
                            reward += 0.5 # Exploitation win
                        elif my_strat == "DEFECT" and other_strat == "DEFECT":
                            reward -= 0.2 # Both lose
                            
            # Penalty for Isolation
            if min_dist > 20:
                reward -= 0.01

        elif self.phase == "CIVILIZATION":
            # Survival Baseline
            reward += 0.01
            
            # 1. Asset Reward (Incentivize Crafting)
            # Check for Stone Blocks in inventory
            blocks = sum(item['count'] for item in self.agent.inventory if item['item']['name'] == 'Stone Block')
            if blocks > 0:
                reward += (blocks * 0.1) # Encourages hoarding blocks -> Crafting from stone
                
            # 2. Construction Reward (Incentivize Building)
            # Scan 5x5 around agent for "Wall" items (Vision channel 2? No, vision 2 is resources)
            # We need to check actual items.
            wall_count = 0
            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    scan_x, scan_y = self.agent.x + dx, self.agent.y + dy
                    if (scan_x, scan_y) in self.world.items_grid:
                         items = self.world.items_grid[(scan_x, scan_y)]
                         for it in items:
                             if it.name == "Wall":
                                 wall_count += 1
            
            if wall_count > 0:
                reward += (wall_count * 0.2) # Encourages building clusters
            
            # 3. Consumption/Action Reward (The "Do It" Incentive)
            # This is harder without action history in env, but state-based usually suffices eventually.
            # If they build, wall_count goes up -> reward goes up.
            
        return reward
