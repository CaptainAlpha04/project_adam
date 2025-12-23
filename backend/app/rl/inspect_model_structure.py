
import gymnasium as gym
from gymnasium import spaces
import numpy as np
from stable_baselines3 import PPO

# 1. Define Dummy Env with exact same spaces as SamsaraEnv
class DummySamsaraEnv(gym.Env):
    def __init__(self):
        super().__init__()
        self.action_space = spaces.Discrete(7)
        
        # Vision Grid: 7x7 View (Radius 3)
        grid_size = 7
        
        self.observation_space = spaces.Dict({
            "vision": spaces.Box(low=0, high=3, shape=(4, grid_size, grid_size), dtype=np.uint8),
            "internal": spaces.Box(low=0, high=1, shape=(5,), dtype=np.float32) 
        })
        
    def reset(self, seed=None, options=None):
        return self.observation_space.sample(), {}
    def step(self, action):
        return self.observation_space.sample(), 0, False, False, {}

# 2. Instantiate Model
env = DummySamsaraEnv()
model = PPO("MultiInputPolicy", env, verbose=1)

# 3. Print Architecture
print("\n--- SOUL NETWORK ARCHITECTURE ---\n")
print(model.policy)
