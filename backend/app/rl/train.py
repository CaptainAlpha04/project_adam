import os
import time
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from .envs import MovementEnv
from .callbacks import RuhCallback

def train_samsara(generations=10, steps_per_gen=10000):
    """
    Implements the Samsara Protocol:
    1. Birth (Load Model)
    2. Life (Train)
    3. Death (Save Model)
    """
    model_path = "adam_soul"
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Create Environment
    env = make_vec_env(MovementEnv, n_envs=1)
    
    # Initialize Ruh Callback
    # Obs dim 77, Action dim 6
    ruh_callback = RuhCallback(obs_dim=77, action_dim=6)
    
    # Initialize Soul (Model)
    if os.path.exists(f"{model_path}.zip"):
        print("--- REBIRTH: Loading existing Soul ---")
        model = PPO.load(model_path, env=env)
    else:
        print("--- GENESIS: Creating new Soul ---")
        model = PPO("MlpPolicy", env, verbose=1)
        
    for gen in range(generations):
        print(f"\n=== GENERATION {gen+1} START ===")
        
        # Train (The Life)
        model.learn(total_timesteps=steps_per_gen, reset_num_timesteps=False, callback=ruh_callback)
        
        # Save (The Death)
        model.save(model_path)
        print(f"=== GENERATION {gen+1} END (Soul Saved) ===\n")
        
    print("Samsara Cycle Complete.")
    return model

if __name__ == "__main__":
    train_samsara()
