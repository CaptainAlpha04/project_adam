from dataclasses import dataclass
import uuid
import numpy as np

@dataclass
class Animal:
    x: int
    y: int
    type: str # 'herbivore', 'carnivore'
    energy: float = 1.0
    id: str = None

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())

    def act(self, world):
        # Simple AI
        if self.type == 'herbivore':
            self._flee_or_graze(world)
        elif self.type == 'carnivore':
            self._hunt(world)

    def _flee_or_graze(self, world):
        # Check for nearby agents (predators)
        nearby_agents = self._get_nearby_agents(world, radius=10)
        if nearby_agents:
            # Flee from closest agent
            closest = nearby_agents[0]
            dx = self.x - closest.x
            dy = self.y - closest.y
            # Normalize and move away
            if abs(dx) > abs(dy):
                move_x = 1 if dx > 0 else -1
                move_y = 0
            else:
                move_x = 0
                move_y = 1 if dy > 0 else -1
            world.move_animal(self.id, move_x, move_y)
        else:
            # Herd Behavior: Flocking
            # 1. Alignment/Cohesion: Move towards center of nearby herbivores
            nearby_herbivores = self._get_nearby_animals(world, radius=10, type_filter='herbivore')
            if nearby_herbivores:
                avg_x = sum(a.x for a in nearby_herbivores) / len(nearby_herbivores)
                avg_y = sum(a.y for a in nearby_herbivores) / len(nearby_herbivores)
                
                dx = avg_x - self.x
                dy = avg_y - self.y
                
                # Move towards herd center
                if abs(dx) > abs(dy):
                    move_x = 1 if dx > 0 else -1
                    move_y = 0
                else:
                    move_x = 0
                    move_y = 1 if dy > 0 else -1
                
                # Add some randomness to avoid getting stuck
                if np.random.random() < 0.2:
                    move_x = np.random.randint(-1, 2)
                    move_y = np.random.randint(-1, 2)
                
                world.move_animal(self.id, move_x, move_y)
            else:
                # Random graze
                if np.random.random() < 0.2:
                    move_x = np.random.randint(-1, 2)
                    move_y = np.random.randint(-1, 2)
                    world.move_animal(self.id, move_x, move_y)

    def _hunt(self, world):
        # Check for nearby agents (prey)
        nearby_agents = self._get_nearby_agents(world, radius=8)
        if nearby_agents:
            # Chase closest agent
            closest = nearby_agents[0]
            dist = np.sqrt((closest.x - self.x)**2 + (closest.y - self.y)**2)
            
            if dist < 1.5:
                # Kill the agent
                closest.die(world, "being eaten by a carnivore")
                self.energy = min(1.0, self.energy + 0.5)
                return

            dx = closest.x - self.x
            dy = closest.y - self.y
            
            if abs(dx) > abs(dy):
                move_x = 1 if dx > 0 else -1
                move_y = 0
            else:
                move_x = 0
                move_y = 1 if dy > 0 else -1
            world.move_animal(self.id, move_x, move_y)
        else:
             # Solitary / Forest Preference
            # Try to stay in Forest (Terrain 3)
            current_terrain = world.terrain_grid[self.y][self.x]
            if current_terrain != 3:
                # Move randomly to find forest? Or just random wander
                move_x = np.random.randint(-1, 2)
                move_y = np.random.randint(-1, 2)
                world.move_animal(self.id, move_x, move_y)
            else:
                # Already in forest, stay put mostly, or patrol
                if np.random.random() < 0.1:
                    move_x = np.random.randint(-1, 2)
                    move_y = np.random.randint(-1, 2)
                    world.move_animal(self.id, move_x, move_y)

    def _get_nearby_animals(self, world, radius, type_filter):
        animals = []
        for animal in world.animals:
            if animal.id == self.id: continue
            if animal.type != type_filter: continue
            dist = np.sqrt((animal.x - self.x)**2 + (animal.y - self.y)**2)
            if dist < radius:
                animals.append(animal)
        return animals

    def _get_nearby_agents(self, world, radius):
        # Inefficient O(N), but fine for small N
        agents = []
        for agent in world.agents.values():
            dist = np.sqrt((agent.x - self.x)**2 + (agent.y - self.y)**2)
            if dist < radius:
                agents.append(agent)
        agents.sort(key=lambda a: np.sqrt((a.x - self.x)**2 + (a.y - self.y)**2))
        return agents


    def die(self, world):
        if self in world.animals:
            world.animals.remove(self)
            # Drop meat
            from .item import Item
            import uuid
            meat = Item(id=f"meat_{uuid.uuid4()}", name="Meat", weight=0.5, hardness=0.1, durability=0.1, tags=["food", "consumable"])
            world._add_item(self.x, self.y, meat)
            
            # Drop Leather (New)
            leather = Item(id=f"leather_{uuid.uuid4()}", name="Leather", weight=0.2, hardness=0.3, durability=0.5, tags=["material", "craftable"])
            world._add_item(self.x, self.y, leather)

    def to_dict(self):
        return {
            "id": self.id,
            "x": int(self.x),
            "y": int(self.y),
            "type": self.type,
            "energy": float(self.energy)
        }
