import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

class RuhNetwork(nn.Module):
    """
    The Witness (Ruh).
    A World Model that observes the Nafs (Agent) and the World.
    Objective: Minimize Prediction Error (Understanding).
    """
    def __init__(self, obs_dim, action_dim, hidden_dim=64):
        super(RuhNetwork, self).__init__()
        
        # Encoder (Compresses Reality)
        self.encoder = nn.Sequential(
            nn.Linear(obs_dim + action_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim)
        )
        
        # Predictor (Foresees Future)
        self.predictor = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, obs_dim) # Predicts next observation
        )
        
        self.optimizer = optim.Adam(self.parameters(), lr=1e-3)
        self.loss_fn = nn.MSELoss()
        
    def forward(self, obs, action):
        # Concatenate Observation and Action
        x = torch.cat([obs, action], dim=-1)
        embedding = self.encoder(x)
        next_obs_pred = self.predictor(embedding)
        return next_obs_pred, embedding

    def train_step(self, obs, action, next_obs):
        self.train()
        self.optimizer.zero_grad()
        
        pred, _ = self(obs, action)
        loss = self.loss_fn(pred, next_obs)
        
        loss.backward()
        self.optimizer.step()
        
        return loss.item()
