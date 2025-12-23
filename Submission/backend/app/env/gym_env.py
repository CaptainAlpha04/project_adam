import gymnasium as gym
from gymnasium import spaces
import numpy as np
from .world import World
from ..agents.agent import Agent

class ProjectAdamEnv(gym.Env):
    """
    Custom Environment that follows gym interface.
    This environment manages the World and allows an RL agent to control a specific agent in the world.
    For multi-agent, we might need to wrap this or iterate.
    """
    metadata = {'render.modes': ['human']}

    def __init__(self, world: World, agent_id: str):
        super(ProjectAdamEnv, self).__init__()
        self.world = world
        self.agent_id = agent_id
        
        # Define action and observation space
        # Actions: 0: Up, 1: Down, 2: Left, 3: Right, 4: Gather, 5: Rest
        self.action_space = spaces.Discrete(6)
        
        # Observation: Local grid (3x3) around agent + internal state
        # Simplified for now: Flattened local grid terrain types (integer encoded) + hunger/energy
        self.observation_space = spaces.Box(low=0, high=1, shape=(11,), dtype=np.float32)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        # In a persistent world, reset might just mean respawning the agent or resetting its state
        # For training, we might reset the whole world, but here we share the world.
        agent = self.world.agents.get(self.agent_id)
        if agent:
            agent.state.hunger = 0
            agent.state.energy = 1
        
        return self._get_obs(), {}

    def step(self, action):
        agent = self.world.agents.get(self.agent_id)
        if not agent:
            return self._get_obs(), 0, True, False, {}

        # Execute action
        agent.act(action, self.world)
        
        # Calculate reward
        reward = self._calculate_reward(agent)
        
        # Check done
        terminated = agent.state.health <= 0
        truncated = False
        
        return self._get_obs(), reward, terminated, truncated, {}

    def _get_obs(self):
        agent = self.world.agents.get(self.agent_id)
        if not agent:
            return np.zeros(11, dtype=np.float32)
            
        # Get local 3x3 grid
        # This is a placeholder for actual local perception
        # We need to encode terrain types to numbers
        obs = []
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                tile = self.world.get_tile(agent.x + dx, agent.y + dy)
                if tile:
                    # Simple encoding: water=0, grass=1, etc.
                    # For now just random or 0/1
                    obs.append(0.5) 
                else:
                    obs.append(0.0) # Out of bounds
        
        # Add internal state
        obs.append(agent.state.hunger)
        obs.append(agent.state.energy)
        
        return np.array(obs, dtype=np.float32)

    def _calculate_reward(self, agent):
        # Basic survival reward
        reward = 0.1 # Alive bonus
        
        # Penalty for hunger
        if agent.state.hunger > 0.8:
            reward -= 0.1
            
        # Reward for gathering (if inventory increased)
        # This requires tracking state change, simplified here
        return reward

    def render(self, mode='human'):
        pass
