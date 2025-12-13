import threading
import time
import socketio
import asyncio
from typing import Optional
from .train import train_samsara
from .callbacks import RuhCallback
from stable_baselines3.common.callbacks import BaseCallback

# Global Socket.IO Server (will be initialized in main.py)
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

class SocketCallback(BaseCallback):
    """
    Callback to emit training stats to frontend via Socket.IO
    """
    def __init__(self, verbose=0):
        super(SocketCallback, self).__init__(verbose)
        self.last_time = time.time()
        
    def _on_step(self) -> bool:
        # Check for stop flag
        if TrainingManager.should_stop:
            return False
            
        # Emit every N steps or time interval
        if time.time() - self.last_time > 0.5: # 2 FPS updates
            self.last_time = time.time()
            
            # Gather stats
            reward = self.locals.get('rewards', [0])[0]
            # loss = ... (hard to get directly from locals in SB3 without logger hacking)
            
            # Get Map State from Env
            env = self.training_env.envs[0].unwrapped
            agent = env.agent
            
            # Construct Map Data
            map_data = {
                'width': env.width,
                'height': env.height,
                'agent': {'x': agent.x, 'y': agent.y},
                'food': [{'x': x, 'y': y} for x, y in env.world.food_grid],
                'items': [{'x': x, 'y': y, 'type': d['type']} for (x, y), d in env.world.items_grid.items()],
                'others': [{'x': a.x, 'y': a.y} for a in env.world.agents.values() if a.id != agent.id]
            }
            
            # Emit (Async in thread is tricky, use run_coroutine_threadsafe if loop exists, 
            # but for simplicity with python-socketio in thread, we might need a sync wrapper or just fire and forget)
            # Actually, sio.emit is async. We are in a sync thread (training).
            # We need to bridge this.
            
            asyncio.run_coroutine_threadsafe(
                sio.emit('training_update', {
                    'step': self.num_timesteps,
                    'reward': float(reward),
                    'map': map_data
                }),
                TrainingManager.loop
            )
            
        return True

class TrainingManager:
    thread: Optional[threading.Thread] = None
    should_stop: bool = False
    loop = None # Asyncio loop reference

    @staticmethod
    def start_training(scenario: str, generations: int):
        if TrainingManager.thread and TrainingManager.thread.is_alive():
            return False
            
        TrainingManager.should_stop = False
        TrainingManager.loop = asyncio.get_event_loop()
        
        def run():
            print(f"Starting training for {scenario}...")
            import os
            from stable_baselines3 import PPO
            from stable_baselines3.common.env_util import make_vec_env
            from stable_baselines3.common.callbacks import CallbackList
            from .envs import MovementEnv, CraftingEnv, SocialEnv
            from .callbacks import RuhCallback
            
            env_class = MovementEnv
            if scenario == 'crafting':
                env_class = CraftingEnv
            elif scenario == 'social':
                env_class = SocialEnv
            
            env = make_vec_env(env_class, n_envs=1)
            
            # Samsara: Load Soul if exists
            model_path = f"adam_soul_{scenario}"
            if os.path.exists(f"{model_path}.zip"):
                print(f"--- REBIRTH: Loading existing Soul for {scenario} ---")
                model = PPO.load(model_path, env=env)
            else:
                print(f"--- GENESIS: Creating new Soul for {scenario} ---")
                model = PPO("MlpPolicy", env, verbose=1)
            
            # Callbacks
            socket_cb = SocketCallback()
            ruh_cb = RuhCallback(obs_dim=77, action_dim=6)
            callbacks = CallbackList([socket_cb, ruh_cb])
            
            try:
                # Train (The Life)
                model.learn(total_timesteps=10000 * generations, callback=callbacks)
                
                # Save (The Death)
                model.save(model_path)
                print(f"--- SOUL SAVED: {model_path} ---")
                
            except Exception as e:
                print(f"Training interrupted or error: {e}")
                # Try to save even on interrupt
                model.save(model_path)
                print(f"--- SOUL SAVED (Emergency): {model_path} ---")
                
            print("Training finished.")

        TrainingManager.thread = threading.Thread(target=run)
        TrainingManager.thread.start()
        return True

    @staticmethod
    def stop_training():
        TrainingManager.should_stop = True
        if TrainingManager.thread:
            TrainingManager.thread.join(timeout=2.0)
        return True
