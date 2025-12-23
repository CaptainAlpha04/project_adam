from dataclasses import dataclass
import numpy as np
from typing import List, Dict, Optional
from typing import List, Dict, Optional
from .item import Item
from ..social.tribe import Tribe

class World:
    def __init__(self, width: int, height: int, seed: int = 42, config: Dict = None):
        self.width = width
        self.height = height
        self.seed = seed
        self.config = config or {
            "hunger_rate": 0.002,
            "resource_growth_rate": 1.0,
            "initial_agent_count": 10
        }
        self.agents = {} # id -> Agent
        self.animals = [] # List[Animal]
        self.terrain_grid = np.zeros((height, width), dtype=int) # 0: Water, 1: Sand, 2: Grass, 3: Forest, 4: Mountain, 5: Snow
        self.items_grid = {} # (x,y) -> [Item]
        self.tribes = {} # id -> Tribe
        self.time_step = 0
        self.generation = 1
        self.trade_history = [] # List of trade events
        
        # Terrain Generation (Perlin Noise)
        self._generate_terrain()
        
    def _generate_terrain(self):
        import noise
        # Height Map
        scale = 20.0 # Smaller scale for more variation in small world
        octaves = 6
        persistence = 0.5
        lacunarity = 2.0
        seed = self.seed
        
        # Moisture Map
        moisture_seed = self.seed + 100
        
        self.height_map = np.zeros((self.height, self.width))
        
        for y in range(self.height):
            for x in range(self.width):
                # Force Water Boundary
                if x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1:
                    self.terrain_grid[y][x] = 0 # Water
                    continue
                
                # Height Noise
                nx = x/scale
                ny = y/scale
                h = noise.pnoise2(nx, ny, octaves=octaves, persistence=persistence, lacunarity=lacunarity, repeatx=self.width, repeaty=self.height, base=seed)
                
                self.height_map[y][x] = h
                
                # Moisture Noise
                m = noise.pnoise2(nx, ny, octaves=4, persistence=0.5, lacunarity=2.0, repeatx=self.width, repeaty=self.height, base=moisture_seed)
                
                # Terrain Logic
                if h < -0.1:
                    self.terrain_grid[y][x] = 0 # Water
                elif h < 0.0:
                    self.terrain_grid[y][x] = 1 # Sand (Beach)
                else:
                    # Land
                    if h > 0.35: # Mountain Range (Lowered threshold)
                        if h > 0.6:
                            self.terrain_grid[y][x] = 5 # Snow (Peaks)
                        else:
                            self.terrain_grid[y][x] = 4 # Mountain
                            # Stone chance
                            if np.random.random() < 0.4:
                                self._add_item(x, y, Item(id=f"stone_{x}_{y}", name="Stone", weight=2.0, hardness=0.9, durability=1.0, tags=["heavy", "material"]))
                    else:
                        # Flat/Hilly
                        if m < -0.15:
                            self.terrain_grid[y][x] = 1 # Sand (Desert)
                        elif m < 0.15:
                            self.terrain_grid[y][x] = 2 # Grass
                            # Fruit chance
                            if np.random.random() < 0.005:
                                self._add_item(x, y, Item(id=f"fruit_{x}_{y}", name="Fruit", weight=0.1, hardness=0.1, durability=0.1, tags=["food", "consumable", "red"]))
                        else:
                            self.terrain_grid[y][x] = 3 # Forest
                            # Wood chance
                            if np.random.random() < 0.6:
                                self._add_item(x, y, Item(id=f"wood_{x}_{y}", name="Wood", weight=1.0, hardness=0.5, durability=1.0, tags=["flammable", "material"]))

    def respawn_resources(self):
        """Respawn resources based on time step and config."""
        rate_mult = self.config.get("resource_growth_rate", 1.0)
        
        # Base Intervals (at rate=1.0)
        fruit_interval = 1000
        wood_interval = 60000
        stone_interval = 120000
        
        # Adjusted Intervals (Higher rate = Smaller interval)
        # Avoid division by zero
        if rate_mult <= 0: rate_mult = 0.001
        
        fruit_mod = int(fruit_interval / rate_mult)
        wood_mod = int(wood_interval / rate_mult)
        stone_mod = int(stone_interval / rate_mult)
        
        # Fruits
        if self.time_step % max(10, fruit_mod) == 0:
            self._spawn_random_items("Fruit", 0.02 * rate_mult, [2], ["food", "consumable", "red"])
        
        # Trees (Wood)
        if self.time_step % max(100, wood_mod) == 0:
            self._spawn_random_items("Wood", 0.15 * rate_mult, [3], ["flammable", "material"])

        # Rocks (Stone)
        if self.time_step % max(500, stone_mod) == 0:
            self._spawn_random_items("Stone", 0.075, [4], ["heavy", "material"])

        # Animals: Every 400 steps (average of 300-500)
        if self.time_step % 6000 == 0:
            self._spawn_animals()

    def _spawn_random_items(self, name, chance, terrain_types, tags):
        for y in range(self.height):
            for x in range(self.width):
                # Force Water Boundary
                if x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1:
                    self.terrain_grid[y][x] = 0 # Water
                    continue
                if self.terrain_grid[y][x] in terrain_types:
                    if np.random.random() < chance:
                        # Only add if empty? Or just add more? Let's add more.
                        self._add_item(x, y, Item(id=f"{name}_{x}_{y}_{self.time_step}", name=name, weight=1.0, hardness=1.0, durability=1.0, tags=tags))

    def _spawn_animals(self):
        from .animals import Animal
        # Spawn a batch of animals
        for _ in range(20):
            # Herbivores (Herd logic handled in movement, just spawn randomly for now)
            attempts = 0
            while attempts < 100:
                x, y = np.random.randint(0, self.width), np.random.randint(0, self.height)
                if self.terrain_grid[y][x] != 0:  # Not water
                    self.animals.append(Animal(x=x, y=y, type='herbivore'))
                    break
                attempts += 1
        
        for _ in range(5):
            # Carnivores
            attempts = 0
            while attempts < 100:
                x, y = np.random.randint(0, self.width), np.random.randint(0, self.height)
                if self.terrain_grid[y][x] != 0:  # Not water
                    self.animals.append(Animal(x=x, y=y, type='carnivore'))
                    break
                attempts += 1

    def _add_item(self, x: int, y: int, item: Item):
        if (x, y) not in self.items_grid:
            self.items_grid[(x, y)] = []
        self.items_grid[(x, y)].append(item)

    def remove_item(self, x: int, y: int, item: Item):
        if (x, y) in self.items_grid:
            if item in self.items_grid[(x, y)]:
                self.items_grid[(x, y)].remove(item)
                if not self.items_grid[(x, y)]:
                    del self.items_grid[(x, y)]

    def get_tile_info(self, x: int, y: int) -> Dict:
        """Returns a dict representation of a tile (for API/Agents)."""
        if 0 <= x < self.width and 0 <= y < self.height:
            terrain_id = self.terrain_grid[y][x]
            terrain_map = {0: 'water', 1: 'sand', 2: 'grass', 3: 'forest', 4: 'mountain', 5: 'snow'}
            return {
                "x": x,
                "y": y,
                "terrain_type": terrain_map[terrain_id],
                "items": [item.to_dict() for item in self.items_grid.get((x, y), [])],
                "agent_id": self._get_agent_at(x, y)
            }
        return None


    def add_agent(self, agent):
        # Clustered Spawning
        # Spawn around center (width/2, height/2) with radius ~40
        center_x = self.width // 2
        center_y = self.height // 2
        
        while True:
            # Random point in circle
            angle = np.random.uniform(0, 2 * np.pi)
            r = np.random.uniform(0, 40) # 40 block radius
            
            x = int(center_x + r * np.cos(angle))
            y = int(center_y + r * np.sin(angle))
            
            # Clamp to bounds
            x = max(0, min(x, self.width - 1))
            y = max(0, min(y, self.height - 1))
            
            if self.terrain_grid[y][x] != 0: # Not water
                agent.x = x
                agent.y = y
                break
        self.agents[agent.id] = agent

    def move_agent(self, agent_id: str, dx: int, dy: int) -> bool:
        agent = self.agents.get(agent_id)
        if not agent:
            return False

        new_x = agent.x + dx
        new_y = agent.y + dy
        
        if not (0 <= new_x < self.width and 0 <= new_y < self.height):
            return False

        # Collision check
        if self.terrain_grid[new_y][new_x] == 0: # Water
            return False
        if self._get_agent_at(new_x, new_y):
            return False

        agent.x = new_x
        agent.y = new_y
        return True

    def move_animal(self, animal_id: str, dx: int, dy: int) -> bool:
        # Find animal (inefficient list search, optimize later)
        animal = next((a for a in self.animals if a.id == animal_id), None)
        if not animal:
            return False

        new_x = animal.x + dx
        new_y = animal.y + dy
        
        if not (0 <= new_x < self.width and 0 <= new_y < self.height):
            return False

        # Collision check (can't move into water)
        if self.terrain_grid[new_y][new_x] == 0: # Water
            return False

        animal.x = new_x
        animal.y = new_y
        return True


        """Returns a simplified state representation for the frontend."""
        # Day/Night Cycle (Scale: 1 day = 24 steps? No, let's say 1000 steps = 1 day)
        # 0-500: Day, 500-1000: Night
        day_progress = self.time_step % 1000
        is_day = day_progress < 500
        
        return {
            "width": int(self.width),
            "height": int(self.height),
            "time_step": int(self.time_step),
            "is_day": is_day, # For frontend lighting
            "terrain": self.terrain_grid.tolist(), 
            "items": [
                {**item.to_dict(), "x": int(k[0]), "y": int(k[1])} 
                for k, v in self.items_grid.items() 
                for item in v
            ],
            "agents": [agent.to_dict(self) for agent in self.agents.values()],
            "animals": [animal.to_dict() for animal in self.animals],
            "logs": getattr(self, 'logs', []),
            "generation": self.generation
        }

    def spawn_child(self, p1, p2):
        """Spawns a child from two parents immediately in the world."""
        from ..agents.agent import Agent, PERSONALITY_TRAITS, NAMES_MALE, NAMES_FEMALE, Soul
        import uuid
        
        # 1. Anti-Stacking Logistics
        # Find a free spot near p1
        spawn_x, spawn_y = p1.x, p1.y
        found_spot = False
        
        # Spiral search for empty spot
        for r in range(1, 5):
            for dy in range(-r, r+1):
                for dx in range(-r, r+1):
                    tx, ty = p1.x + dx, p1.y + dy
                    if 0 <= tx < self.width and 0 <= ty < self.height:
                        if self.terrain_grid[ty][tx] != 0: # Not water
                             if not self._get_agent_at(tx, ty):
                                 spawn_x, spawn_y = tx, ty
                                 found_spot = True
                                 break
                if found_spot: break
            if found_spot: break
            
        if not found_spot:
            self.log_event(f"Birth failed: No room for child of {p1.attributes.name}.")
            return

        child_gender = np.random.choice(["male", "female"])
        
        # New Soul (Fresh Start for in-game birth)
        # But inherit Karma average
        avg_karma = (p1.ruh.soul.karma + p2.ruh.soul.karma) / 2.0
        child_soul = Soul(id=str(uuid.uuid4()), memories=[], karma=avg_karma, past_lives=0)
        
        child = Agent(x=spawn_x, y=spawn_y, gender=child_gender, soul=child_soul, birth_time=self.time_step)
        
        # Genetics: Personality
        child_p_vector = {}
        for trait in PERSONALITY_TRAITS:
            val = (p1.attributes.personality_vector[trait] + p2.attributes.personality_vector[trait]) / 2.0
            if np.random.random() < 0.1: val += np.random.normal(0, 0.1)
            child_p_vector[trait] = float(np.clip(val, 0.0, 1.0))
        
        child.attributes.personality_vector = child_p_vector
        child.attributes.generation = max(p1.attributes.generation, p2.attributes.generation) + 1
        
        # 2. Family Tree
        child.attributes.parents = [p1.id, p2.id]
        
        # 3. Tribe Logic (Genesis)
        # If both parents are Nomads (no tribe), create a NEW Tribe.
        tribe_id = None
        
        if not p1.attributes.tribe_id and not p2.attributes.tribe_id:
            # Genesis
            # Determine Leader (Stronger Personality)
            score1 = p1.attributes.aggression + p1.attributes.personality_vector["Social"]
            score2 = p2.attributes.aggression + p2.attributes.personality_vector["Social"]
            
            leader = p1 if score1 >= score2 else p2
            tribe_name = f"Clan of {leader.attributes.name}"
            tribe = self.create_tribe(tribe_name, leader.id)
            tribe_id = tribe.id
            
            # Parents join
            p1.attributes.tribe_id = tribe_id
            p1.attributes.leader_id = leader.id
            p2.attributes.tribe_id = tribe_id
            p2.attributes.leader_id = leader.id
            
            self.log_event(f"Tribe Genesis: {tribe_name} founded by {leader.attributes.name} upon birth of first child.")
            
        elif p1.attributes.tribe_id:
            tribe_id = p1.attributes.tribe_id
        elif p2.attributes.tribe_id:
            tribe_id = p2.attributes.tribe_id
            
        if tribe_id:
            child.attributes.tribe_id = tribe_id
            # Inherit leader from tribe
            tribe = self.tribes.get(tribe_id)
            if tribe:
                child.attributes.leader_id = tribe.leader_id
        
        # Add to world
        self.agents[child.id] = child
        
        # Link Parents
        p1.attributes.children.append(child.id)
        p2.attributes.children.append(child.id)
        
        self.log_event(f"Birth: {child.attributes.name} (Gen {child.attributes.generation}) born to {p1.attributes.name} & {p2.attributes.name}.")

    def evolve_generation(self):
        """
        Legacy method. Disabled to enforce continuous simulation.
        New agents only appear via biological reproduction.
        """
        self.log_event("Evolution is continuous. No generation resets.")
        pass

    def create_tribe(self, name: str, leader_id: str) -> Tribe:
        import uuid
        tribe = Tribe(name=name)
        tribe.set_leader(leader_id)
        self.tribes[tribe.id] = tribe
        self.log_event(f"Tribe Founded: {name} by {self.agents[leader_id].attributes.name}")
        return tribe

    def join_tribe(self, agent_id: str, tribe_id: str):
        tribe = self.tribes.get(tribe_id)
        if tribe:
            # Remove from old tribe?
            old_tribe = self.get_agent_tribe(agent_id)
            if old_tribe:
                 old_tribe.remove_member(agent_id)
            
            tribe.add_member(agent_id)
            # Update Agent Attr
            agent = self.agents.get(agent_id)
            if agent:
                agent.attributes.tribe_id = tribe_id
            self.log_event(f"{agent.attributes.name} joined {tribe.name}.")

    def get_agent_tribe(self, agent_id: str) -> Optional[Tribe]:
        agent = self.agents.get(agent_id)
        if agent and hasattr(agent.attributes, 'tribe_id') and agent.attributes.tribe_id:
             return self.tribes.get(agent.attributes.tribe_id)
        return None

    def log_event(self, message: str):
        # Keep only last 50 logs
        if not hasattr(self, 'logs'):
            self.logs = []
        msg = f"[Step {self.time_step}] {message}"
        self.logs.append(msg)
        print(msg)
        if len(self.logs) > 50:
            self.logs.pop(0)

    def log_trade(self, protagonist, target, offer, request, mode):
        # 1. Add to structured history for analysis
        event = {
            "step": self.time_step,
            "initiator_id": protagonist.id,
            "initiator_name": protagonist.attributes.name,
            "target_id": target.id,
            "target_name": target.attributes.name,
            "offer": offer['name'] if offer else "Nothing",
            "request": request if request else "Nothing",
            "mode": mode
        }
        self.trade_history.append(event)
        if len(self.trade_history) > 1000:
            self.trade_history.pop(0)

        # 2. Log string for Frontend Notification
        action = "gifted" if mode == 'gift' else "traded"
        if mode == 'gift':
             self.log_event(f"{protagonist.attributes.name} gifted {offer['name']} to {target.attributes.name}.")
        else:
             self.log_event(f"{protagonist.attributes.name} traded {offer['name']} with {target.attributes.name} for {request}.")
    
    def _get_agent_at(self, x, y):
        for a in self.agents.values():
            if int(a.x) == x and int(a.y) == y:
                return a
        return None
