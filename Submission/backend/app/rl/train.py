import os
import time
import argparse
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.callbacks import CheckpointCallback
from .envs import SamsaraEnv

def train_samsara(total_generations=100, steps_per_gen=20480, start_phase=None, force_phase=None):
    """
    Implements the Samsara Protocol:
    The model ("Soul") is passed down from generation to generation.
    """
    model_path = "adam_soul"
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    print("--- INITIATING SAMSARA PROTOCOL ---")
    
    current_gen = 0
    # Try to determine current generation from saved files if possible
    # (Simple logic: look for highest gen file)
    try:
        existing_gens = [int(f.split('_gen_')[1].replace('.zip', '')) for f in os.listdir('.') 
                        if f.startswith(f"{model_path}_gen_") and f.endswith('.zip')]
        if existing_gens:
            current_gen = max(existing_gens) + 1
            print(f"Resuming from Generation {current_gen}")
    except Exception as e:
        print(f"Correction: Could not parse existing generations ({e}). Starting fresh or from main zip.")
    
    while current_gen < total_generations:
        # Determine Phase
        phase = "SURVIVAL"
        
        if force_phase:
            phase = force_phase
        else:
            # Auto Curriculum
            if current_gen > 20: phase = "GATHERING"
            if current_gen > 50: phase = "SOCIETY"
            
            # Start Phase override (Manual jump start)
            if start_phase and current_gen == 0:
                phase = start_phase
        
        print(f"\n=== GENERATION {current_gen+1} (Phase: {phase}) ===")
        
        # Re-create environment per generation
        env = make_vec_env(lambda: SamsaraEnv(phase=phase), n_envs=4) # Parallel training
        
        if os.path.exists(f"{model_path}.zip"):
            try:
                model = PPO.load(model_path, env=env)
                print(">> Soul Transmigrated (Model Loaded)")
            except:
                print(">> Soul Corrupted. Rebirthing.")
                model = PPO("MultiInputPolicy", env, verbose=1, 
                            tensorboard_log=log_dir,
                            ent_coef=0.01,
                            learning_rate=0.0003)
        else:
            print(">> Genesis (New Model Created)")
            model = PPO("MultiInputPolicy", env, verbose=1, 
                        tensorboard_log=log_dir,
                        ent_coef=0.01, # Encourage exploration
                        learning_rate=0.0003)
        
        # TRAIN
        print(f">> Living for {steps_per_gen} steps...")
        model.learn(total_timesteps=steps_per_gen, reset_num_timesteps=False)
        
        # SAVE
        model.save(model_path)
        model.save(f"{model_path}_gen_{current_gen}") # History
        print(f">> Death & Rebirth. Soul Saved to {model_path}.zip")
        
        current_gen += 1
        env.close()
        
    print("--- SAMSARA CYCLE COMPLETE ---")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Project Adam Agents (Samsara Protocol)")
    parser.add_argument("--gens", type=int, default=100, help="Total generations to train")
    parser.add_argument("--steps", type=int, default=20480, help="Steps per generation")
    
    # Phase Flags
    parser.add_argument("--phase1", action="store_true", help="Force Phase 1 (Survival)")
    parser.add_argument("--phase2", action="store_true", help="Force Phase 2 (Gathering)")
    parser.add_argument("--phase3", action="store_true", help="Force Phase 3 (Society)")
    parser.add_argument("--phase4", action="store_true", help="Force Phase 4 (Civilization)")
    
    args = parser.parse_args()
    
    force_phase = None
    if args.phase1: force_phase = "SURVIVAL"
    elif args.phase2: force_phase = "GATHERING"
    elif args.phase3: force_phase = "SOCIETY"
    elif args.phase4: force_phase = "CIVILIZATION"
    
    train_samsara(total_generations=args.gens, steps_per_gen=args.steps, force_phase=force_phase)
