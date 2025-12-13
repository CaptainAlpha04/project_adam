import torch
import numpy as np
from stable_baselines3.common.callbacks import BaseCallback
from .ruh import RuhNetwork

class RuhCallback(BaseCallback):
    """
    Callback to train the Ruh (Witness) network.
    """
    def __init__(self, obs_dim, action_dim, verbose=0):
        super(RuhCallback, self).__init__(verbose)
        self.ruh = RuhNetwork(obs_dim, action_dim)
        self.last_obs = None
        self.losses = []

    def _on_step(self) -> bool:
        # Get current observation
        obs = self.locals['new_obs']
        if isinstance(obs, dict):
            # Handle Dict observation if needed, for now assume Box
            return True
            
        # Convert to torch
        obs_tensor = torch.as_tensor(obs, dtype=torch.float32)
        
        # Get action
        actions = self.locals['actions']
        # One-hot encode action if discrete
        action_dim = 6 # Hardcoded for now based on env
        action_tensor = torch.zeros((len(actions), action_dim))
        for i, act in enumerate(actions):
            action_tensor[i][int(act)] = 1.0
            
        # Train Ruh if we have a previous observation
        if self.last_obs is not None:
            loss = self.ruh.train_step(self.last_obs, self.last_action, obs_tensor)
            self.losses.append(loss)
            
            if self.n_calls % 1000 == 0:
                avg_loss = np.mean(self.losses[-1000:])
                print(f"[RUH] Witness Loss: {avg_loss:.4f} (Understanding the Nafs)")
        
        # Store for next step
        self.last_obs = obs_tensor
        self.last_action = action_tensor
        
        return True
