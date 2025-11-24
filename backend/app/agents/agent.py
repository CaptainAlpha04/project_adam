from dataclasses import dataclass, field
from typing import List, Dict, Any
import uuid
import numpy as np

@dataclass
class AgentAttributes:
    name: str
    gender: str # 'male', 'female'
    personality: List[float] # [Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism]
    curiosity: float = 0.5
    honesty: float = 0.5
    metabolism: float = 0.5
    aggression: float = 0.1

@dataclass
class AgentState:
    hunger: float = 0.0
    thirst: float = 0.0
    happiness: float = 0.5
    health: float = 1.0

NAMES_MALE = ["Adam", "Bob", "Charlie", "David", "Ethan", "Frank", "George", "Henry", "Isaac", "Jack"]
NAMES_FEMALE = ["Alice", "Bella", "Clara", "Diana", "Eve", "Fiona", "Grace", "Hannah", "Ivy", "Julia"]

class Agent:
    def __init__(self, x: int, y: int, name: str = None, gender: str = None):
        self.id = str(uuid.uuid4())
        self.x = x
        self.y = y
        
        if gender is None:
            gender = np.random.choice(['male', 'female'])
        
        if name is None:
            if gender == 'male':
                name = np.random.choice(NAMES_MALE)
            else:
                name = np.random.choice(NAMES_FEMALE)
        
        # Personality Vector (Big 5)
        # 0: Openness, 1: Conscientiousness, 2: Extraversion, 3: Agreeableness, 4: Neuroticism
        personality = np.random.random(5).tolist()
        
        self.attributes = AgentAttributes(name=name, 
                                          gender=gender,
                                          personality=personality,
                                          curiosity=np.random.random(),
                                          honesty=np.random.random(),
                                          aggression=np.random.random() if gender == 'male' else np.random.random() * 0.5)
        self.state = AgentState()
        self.inventory: List[Dict] = []
        self.knowledge: List[str] = [] 
        self.equipped_items: List[Dict] = [] 
        
        # New Systems
        self.memory: List[str] = [] # Functional memory (e.g. "Saw fruit at 10,10")
        self.short_term_goal: str = "Survive"
        self.long_term_goal: str = "Thrive"
        self.traits: List[str] = self._derive_traits(personality)
        
        # Movement tracking
        self.last_x, self.last_y = x, y

    def _derive_traits(self, p: List[float]) -> List[str]:
        traits = []
        if p[0] > 0.7: traits.append("Curious")
        if p[0] < 0.3: traits.append("Traditional")
        if p[1] > 0.7: traits.append("Organized")
        if p[1] < 0.3: traits.append("Lazy")
        if p[2] > 0.7: traits.append("Social")
        if p[2] < 0.3: traits.append("Loner")
        if p[3] > 0.7: traits.append("Friendly")
        if p[3] < 0.3: traits.append("Aggressive")
        if p[4] > 0.7: traits.append("Anxious")
        if p[4] < 0.3: traits.append("Calm")
        return traits

    def to_dict(self):
        return {
            "id": self.id,
            "x": int(self.x),
            "y": int(self.y),
            "attributes": self.attributes.__dict__,
            "state": self.state.__dict__,
            "inventory": self.inventory,
            "knowledge": self.knowledge,
            "diary": getattr(self, 'diary', []),
            "traits": self.traits,
            "short_term_goal": self.short_term_goal,
            "long_term_goal": self.long_term_goal,
            "memory": self.memory[-10:] # Last 10 memories
        }

    def log_diary(self, entry: str):
        if not hasattr(self, 'diary'):
            self.diary = []
        self.diary.append(f"[Step {len(self.diary)}] {entry}")
        
    def add_memory(self, entry: str):
        self.memory.append(f"[Step {len(getattr(self, 'diary', []))}] {entry}")

    def die(self, world, cause: str):
        world.log_event(f"Agent {self.attributes.name} died of {cause}.")
        if self.id in world.agents:
            del world.agents[self.id]

    def reproduce(self, partner, world):
        # Genetic Algorithm for offspring
        child_gender = np.random.choice(['male', 'female'])
        
        # Mix personalities (average + mutation)
        p1 = np.array(self.attributes.personality)
        p2 = np.array(partner.attributes.personality)
        child_personality = ((p1 + p2) / 2 + np.random.normal(0, 0.1, 5)).clip(0, 1).tolist()
        
        # Name generation (simple)
        child_name = np.random.choice(NAMES_MALE if child_gender == 'male' else NAMES_FEMALE)
        
        child = Agent(x=self.x, y=self.y, name=child_name, gender=child_gender)
        child.attributes.personality = child_personality
        # Inherit some traits
        child.attributes.metabolism = (self.attributes.metabolism + partner.attributes.metabolism) / 2
        
        world.add_agent(child)
        world.log_event(f"{self.attributes.name} and {partner.attributes.name} had a baby: {child_name}!")
        self.log_diary(f"I had a baby named {child_name} with {partner.attributes.name}!")
        self.add_memory(f"Had a child {child_name} with {partner.attributes.name}")
        partner.log_diary(f"I had a baby named {child_name} with {self.attributes.name}!")

    def act(self, action_idx: int, world):
        """
        Executes an action.
        Prioritizes survival > social > exploration.
        """
        # Track last position for movement penalty
        if not hasattr(self, 'last_x'):
            self.last_x, self.last_y = self.x, self.y
        
        # Perception
        perceived = self.perceive(world)
        
        # Check Vitality (Death)
        if self.state.hunger >= 1.0:
            self.die(world, "starvation")
            return
        # Removed Energy check

        # CRITICAL: Flee from carnivores
        nearby_carnivores = []
        for animal in world.animals:
            if animal.type == 'carnivore':
                dist = np.sqrt((self.x - animal.x)**2 + (self.y - animal.y)**2)
                if dist < 10:
                    nearby_carnivores.append((animal, dist))
        
        if nearby_carnivores:
            self.short_term_goal = "Fleeing Predator"
            # Flee from closest carnivore
            nearest_carnivore = min(nearby_carnivores, key=lambda x: x[1])[0]
            dx = self.x - nearest_carnivore.x
            dy = self.y - nearest_carnivore.y
            
            # Move away
            move_x = 1 if dx > 0 else -1 if dx < 0 else np.random.choice([-1, 1])
            move_y = 1 if dy > 0 else -1 if dy < 0 else np.random.choice([-1, 1])
            
            if world.move_agent(self.id, move_x, move_y):
                self.log_diary("I saw a carnivore and ran away!")
            return

        # Survival: Eat if hungry (Priority increased)
        if self.state.hunger > 0.3:
            self.short_term_goal = "Find Food"
            # 1. Check inventory for food
            for i, slot in enumerate(self.inventory):
                if slot['count'] > 0 and "food" in slot['item']['tags']:
                    self.state.hunger = max(0, self.state.hunger - 0.5)
                    slot['count'] -= 1
                    if slot['count'] == 0:
                        self.inventory.pop(i)
                    self.log_diary(f"I ate a {slot['item']['name']} from my bag.")
                    self.short_term_goal = "Eating"
                    return

            # 2. Hunt herbivores if very hungry
            if self.state.hunger > 0.6:
                self.short_term_goal = "Hunting"
                nearby_herbivores = []
                for animal in world.animals:
                    if animal.type == 'herbivore':
                        dist = np.sqrt((self.x - animal.x)**2 + (self.y - animal.y)**2)
                        if dist < 15:
                            nearby_herbivores.append((animal, dist))
                
                if nearby_herbivores:
                    nearest_herbivore = min(nearby_herbivores, key=lambda x: x[1])[0]
                    dist = min(nearby_herbivores, key=lambda x: x[1])[1]
                    
                    if dist < 1.5:
                        # "Catch" the herbivore (simplified)
                        world.animals.remove(nearest_herbivore)
                        self.state.hunger = max(0, self.state.hunger - 0.7)
                        self.log_diary("I caught and ate a herbivore!")
                        self.add_memory("Hunted a herbivore successfully.")
                        return
                    else:
                        # Chase
                        dx = nearest_herbivore.x - self.x
                        dy = nearest_herbivore.y - self.y
                        move_x = 1 if dx > 0 else -1 if dx < 0 else 0
                        move_y = 1 if dy > 0 else -1 if dy < 0 else 0
                        world.move_agent(self.id, move_x, move_y)
                        self.log_diary("I'm chasing a herbivore!")
                        return

            # 3. Look for food in perceived items
            target_item = None
            min_dist = float('inf')
            for item_info in perceived['items']:
                if "food" in item_info['item'].tags:
                    dist = np.sqrt((self.x - item_info['x'])**2 + (self.y - item_info['y'])**2)
                    if dist < min_dist:
                        min_dist = dist
                        target_item = item_info
            
            if target_item:
                if min_dist < 1.5:
                    self.gather(world)
                else:
                    # Move towards item
                    dx = target_item['x'] - self.x
                    dy = target_item['y'] - self.y
                    move_x = 1 if dx > 0 else -1 if dx < 0 else 0
                    move_y = 1 if dy > 0 else -1 if dy < 0 else 0
                    world.move_agent(self.id, move_x, move_y)
                    self.log_diary(f"I saw food and moved towards it.")
                return
            
            # 4. Random search (Explore)
            self.explore(world)
            self.log_diary("I am hungry and looking for food.")
            return

        # Social: Trade or Socialize
        if perceived['agents']:
            # Pick closest agent
            closest_agent = perceived['agents'][0]['agent']
            dist = perceived['agents'][0]['dist']
            
            if dist < 2:
                # Try to trade first if we have needs
                if self.trade(closest_agent, world):
                    self.short_term_goal = "Trading"
                    return
                
                # Otherwise socialize
                if np.random.random() < self.attributes.personality[2]:
                    self.socialize(world)
                    self.short_term_goal = "Socializing"
                    return

        # Exploration/Wander
        self.short_term_goal = "Exploring"
        self.explore(world)
        
        # Metabolism update
        self.state.hunger += 0.005 * self.attributes.metabolism
        # Removed Energy update
        
        # Movement penalty (if stayed in same spot)
        if self.x == self.last_x and self.y == self.last_y:
            self.state.hunger += 0.01 # Increased hunger penalty
            self.state.happiness -= 0.05 # Increased happiness penalty
        
        self.last_x, self.last_y = self.x, self.y

    def perceive(self, world):
        """
        Detects objects within radius 20 with probability decreasing by distance.
        Returns dict of visible agents, animals, items.
        """
        radius = 20
        visible = {'agents': [], 'animals': [], 'items': []}
        
        # Agents
        for other in world.agents.values():
            if other.id == self.id: continue
            dist = np.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
            if dist < radius:
                prob = 1.0 - (dist / radius)
                if np.random.random() < prob:
                    visible['agents'].append({'agent': other, 'dist': dist})
        visible['agents'].sort(key=lambda x: x['dist'])

        # Items (Simplified: check local grid)
        # In a real spatial index this would be faster. For now, scan range.
        # Optimization: Just check current tile and immediate neighbors for now to save perf
        # Or iterate all items if N is small. Let's iterate all items for correctness as requested.
        for pos, items in world.items_grid.items():
            dist = np.sqrt((self.x - pos[0])**2 + (self.y - pos[1])**2)
            if dist < radius:
                 prob = 1.0 - (dist / radius)
                 if np.random.random() < prob:
                     for item in items:
                         visible['items'].append({'item': item, 'x': pos[0], 'y': pos[1], 'dist': dist})
        
        return visible

    def trade(self, partner, world):
        """
        Simple Barter Logic.
        If I have X and need Y, and partner has Y, propose trade.
        Value is based on utility (Hunger -> Food).
        """
        # My Needs
        my_need_food = self.state.hunger > 0.2
        
        # Partner Needs (Estimated or communicated)
        partner_need_food = partner.state.hunger > 0.2
        
        # Check my inventory
        my_food = []
        my_other = []
        for i, slot in enumerate(self.inventory):
            if "food" in slot['item']['tags']:
                my_food.append(i)
            else:
                my_other.append(i)
                
        # Check partner inventory (assuming visible during trade)
        partner_food = []
        partner_other = []
        for i, slot in enumerate(partner.inventory):
            if "food" in slot['item']['tags']:
                partner_food.append(i)
            else:
                partner_other.append(i)
        
        # Scenario 1: I need food, I have other items. Partner has food.
        if my_need_food and partner_food and my_other:
            # Propose: My Item (index 0 of other) for Their Food (index 0 of food)
            # Simple acceptance: If partner doesn't need food desperately, they accept
            if not partner_need_food or len(partner_food) > 1:
                # Execute Trade
                my_item_idx = my_other[0]
                their_item_idx = partner_food[0]
                
                # Swap
                my_slot = self.inventory[my_item_idx]
                their_slot = partner.inventory[their_item_idx]
                
                # Decrement counts (assume trading 1 unit)
                # For simplicity, we just swap the item objects for now if count is 1, or handle split
                # Let's just swap one unit
                
                # Receive
                self.inventory.append({'item': their_slot['item'], 'count': 1})
                their_slot['count'] -= 1
                if their_slot['count'] == 0:
                    partner.inventory.pop(their_item_idx)
                    
                # Give
                partner.inventory.append({'item': my_slot['item'], 'count': 1})
                my_slot['count'] -= 1
                if my_slot['count'] == 0:
                    self.inventory.pop(my_item_idx)
                    
                world.log_event(f"{self.attributes.name} traded with {partner.attributes.name}")
                self.log_diary(f"I traded {my_slot['item']['name']} for food with {partner.attributes.name}.")
                partner.log_diary(f"I traded food for {my_slot['item']['name']} with {self.attributes.name}.")
                return True
                
        return False

    def explore(self, world):
        # Improved Exploration: Momentum
        # If we have a last move direction, try to keep it with high prob
        if not hasattr(self, 'last_dx'):
            self.last_dx = np.random.randint(-1, 2)
            self.last_dx = 1 if self.last_dx == 0 else self.last_dx # Avoid 0 initially
            self.last_dy = np.random.randint(-1, 2)

        # 80% chance to keep direction, 20% to change
        if np.random.random() < 0.8:
            dx, dy = self.last_dx, self.last_dy
        else:
            dx = np.random.randint(-1, 2)
            dy = np.random.randint(-1, 2)
            self.last_dx, self.last_dy = dx, dy
            
        if not world.move_agent(self.id, dx, dy):
            # If blocked, pick new random direction
            self.last_dx = np.random.randint(-1, 2)
            self.last_dy = np.random.randint(-1, 2)
            self.log_diary("I hit a wall and turned.")
        else:
            # self.log_diary(f"I explored.") # Too spammy
            pass

    def socialize(self, world) -> bool:
        # Find nearest agent
        nearest = None
        min_dist = float('inf')
        for other in world.agents.values():
            if other.id == self.id: continue
            dist = np.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
            if dist < min_dist:
                min_dist = dist
                nearest = other
        
        if nearest:
            # If close, stay/talk
            if min_dist <= 2:
                self.log_diary(f"I hung out with {nearest.attributes.name}.")
                
                # Reproduction Logic
                if self.attributes.gender != nearest.attributes.gender:
                    # Simple compatibility check (personality distance)
                    p1 = np.array(self.attributes.personality)
                    p2 = np.array(nearest.attributes.personality)
                    compatibility = 1.0 - np.linalg.norm(p1 - p2) / np.sqrt(5) # 0 to 1
                    
                    if compatibility > 0.7 and np.random.random() < 0.05: # 5% chance if compatible
                        self.reproduce(nearest, world)
                
                return True
            # If far (but within 'sensing' range e.g. 20), move towards
            elif min_dist < 20:
                dx = nearest.x - self.x
                dy = nearest.y - self.y
                move_x = 1 if dx > 0 else -1 if dx < 0 else 0
                move_y = 1 if dy > 0 else -1 if dy < 0 else 0
                world.move_agent(self.id, move_x, move_y)
                self.log_diary(f"I saw {nearest.attributes.name} and moved towards them.")
                return True
        return False

    def explore(self, world):
        # Move in a somewhat consistent direction to explore
        # For now, just random walk but with momentum could be better
        # Let's stick to random for now but log it
        move_x = np.random.randint(-1, 2)
        move_y = np.random.randint(-1, 2)
        if world.move_agent(self.id, move_x, move_y):
            self.log_diary(f"I explored the area.")
        else:
            self.log_diary("I tried to move but was blocked.")

    def rest(self):
        self.state.energy = min(1.0, self.state.energy + 0.1)

    def craft(self, item_name: str, world=None):
        from ..env.item import RECIPES, Item
        recipe = RECIPES.get(item_name)
        if not recipe:
            return False
        
        # Check inventory for components (simplified: just check by name substring or tag)
        # This is a placeholder for complex matching logic
        # For now, we just check if we have 2 items to merge
        if len(self.inventory) >= 2:
            # Consume 2 items and create the new one
            self.inventory.pop(0)
            self.inventory.pop(0)
            
            new_item = Item(id=str(uuid.uuid4()), 
                            name=item_name, 
                            weight=1.0, 
                            hardness=1.0, 
                            durability=1.0, 
                            tags=recipe["tags"])
            self.inventory.append(new_item.to_dict())
            self.knowledge.append(item_name)
            if world:
                world.log_event(f"{self.attributes.name} crafted {item_name}")
            return True
        return False

    def gather(self, world):
        tile_items = world.items_grid.get((self.x, self.y), [])
        if tile_items:
            # Prioritize food if hungry
            target_index = 0
            if self.state.hunger > 0.3:
                for i, item in enumerate(tile_items):
                    if "food" in item.tags:
                        target_index = i
                        break
            
            item = tile_items.pop(target_index)
            
            # Inventory Stacking Logic
            stacked = False
            for slot in self.inventory:
                if slot['item']['name'] == item.name and slot['count'] < 10:
                    slot['count'] += 1
                    stacked = True
                    break
            
            if not stacked:
                if len(self.inventory) < 5:
                    self.inventory.append({'item': item.to_dict(), 'count': 1})
                else:
                    # Inventory full, put back on ground
                    tile_items.append(item)
                    self.log_diary("My bag is full!")
                    return

            # Successfully gathered, remove from world
            world.remove_item(self.x, self.y, item)
            world.log_event(f"{self.attributes.name} gathered {item.name}")
            
            # Specific logging
            if item.name == "Fruit":
                self.log_diary(f"I picked a fruit!")
            elif item.name == "Wood":
                self.log_diary(f"I gathered wood from a tree!")
            elif item.name == "Stone":
                self.log_diary(f"I picked up a rock!")
            else:
                self.log_diary(f"I found a {item.name}!")

    def equip(self, item_index: int):
        if 0 <= item_index < len(self.inventory):
            slot = self.inventory[item_index]
            # Can only equip one item at a time
            if slot['count'] > 0:
                item_dict = slot['item']
                if len(self.equipped_items) < 5:
                    self.equipped_items.append(item_dict)
                    slot['count'] -= 1
                    if slot['count'] == 0:
                        self.inventory.pop(item_index)
                else:
                    pass # Equipped full
