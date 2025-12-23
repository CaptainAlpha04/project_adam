import time
import os
from stable_baselines3 import PPO
from backend.app.rl.envs import MovementEnv

def run_visual_test():
    model_path = "adam_soul"
    
    if not os.path.exists(f"{model_path}.zip"):
        print("No Soul found! Please train the agent first.")
        return

    print("Loading Soul...")
    model = PPO.load(model_path)
    
    env = MovementEnv(render_mode="ascii", width=20, height=20)
    obs, _ = env.reset()
    
    print("Starting Visual Verification...")
    try:
        for _ in range(100):
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, _ = env.step(action)
            
            os.system('cls' if os.name == 'nt' else 'clear')
            env.render()
            print(f"Action: {action}, Reward: {reward:.2f}")
            time.sleep(0.2)
            
            if terminated or truncated:
                obs, _ = env.reset()
                
    except KeyboardInterrupt:
        print("Stopped.")

if __name__ == "__main__":
    run_visual_test()
