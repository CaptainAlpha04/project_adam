from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import uuid
import numpy as np

@dataclass
class AgentAttributes:
    name: str
    gender: str # 'male', 'female'
    personality_vector: Dict[str, float] # 20+ dimensions
    generation: int = 1
    partner_id: Optional[str] = None
    friend_ids: List[str] = None
    values: Dict[str, float] = None # Principles: {"Pacifism": 0.5, "Preservation": 0.8}

    def __post_init__(self):
        if self.friend_ids is None:
            self.friend_ids = []
        if self.values is None:
            self.values = {}
            
    curiosity: float = 0.5 
    honesty: float = 0.5
    metabolism: float = 0.5
    aggression: float = 0.1

PERSONALITY_TRAITS = [
    "Curiosity", "Survival", "Social", "Aggression", "Loyalty", 
    "Independence", "Patience", "Impulsivity", "Creativity", "Logic", 
    "Empathy", "Selfishness", "Bravery", "Caution", "Energy", 
    "Laziness", "Lust", "Greed", "Altruism", "Resilience",
    "Optimism", "Pessimism", "Ambition", "Modesty", "Humor",
    "Seriousness", "Forgiveness", "Vengefulness", "Spirituality", "Skepticism"
]

@dataclass
class Memory:
    type: str # 'event', 'location', 'social'
    description: str
    location: tuple # (x, y)
    time: int
    emotional_impact: float # -1.0 to 1.0
    related_entity_id: Optional[str] = None

@dataclass
class AgentState:
    hunger: float = 0.0
    thirst: float = 0.0
    happiness: float = 0.5
    health: float = 1.0


NAMES_MALE = [
    "Adam", "Bob", "Charlie", "David", "Ethan", "Frank", "George", "Henry", "Isaac", "Jack",
    "Liam", "Noah", "Oliver", "Elijah", "James", "William", "Benjamin", "Lucas", "Mason", "Logan",
    "Alexander", "Sebastian", "Jack", "Aiden", "Owen", "Samuel", "Matthew", "Joseph", "Levi", "Mateo",
    "Daniel", "Michael", "Jackson", "Viktor", "Harry", "Ron", "Albus", "Severus", "Draco", "Neville",
    "Frodo", "Sam", "Merry", "Pippin", "Aragorn", "Legolas", "Gimli", "Boromir", "Gandalf", "Bilbo",
    "Thor", "Loki", "Odin", "Tony", "Steve", "Bruce", "Clint", "Natasha", "Peter", "Stephen",
    "Clark", "Bruce", "Diana", "Barry", "Arthur", "Victor", "Hal", "John", "Oliver", "Din",
    "Luke", "Han", "Chewie", "Lando", "Kylo", "Finn", "Poe", "Anakin", "Obi-Wan", "Yoda",
    "Mario", "Luigi", "Wario", "Waluigi", "Bowser", "Toad", "Yoshi", "Donkey", "Diddy", "Link",
    "Zelda", "Ganon", "Kirby", "Fox", "Falco", "Slippy", "Peppy", "Wolf", "Captain", "Falcon"
]

NAMES_FEMALE = [
    "Alice", "Bella", "Clara", "Diana", "Eve", "Fiona", "Grace", "Hannah", "Ivy", "Julia",
    "Olivia", "Emma", "Ava", "Charlotte", "Sophia", "Amelia", "Isabella", "Mia", "Evelyn", "Harper",
    "Camila", "Gianna", "Abigail", "Luna", "Ella", "Elizabeth", "Sofia", "Emily", "Avery", "Mila",
    "Scarlett", "Eleanor", "Madison", "Layla", "Penelope", "Aria", "Chloe", "Grace", "Ellie", "Nora",
    "Hermione", "Ginny", "Luna", "Minerva", "Molly", "Bellatrix", "Narcissa", "Lily", "Petunia", "Cho",
    "Galadriel", "Arwen", "Eowyn", "Rosie", "Elanor", "Goldberry", "Lobelia", "Primula", "Melian", "Luthien",
    "Natasha", "Wanda", "Carol", "Hope", "Peggy", "Sharon", "Maria", "Monica", "Kamala", "Jennifer",
    "Lois", "Selina", "Harley", "Pamela", "Barbara", "Cassandra", "Stephanie", "Kate", "Kara", "Mera",
    "Leia", "Padme", "Rey", "Jyn", "Ahsoka", "Sabine", "Hera", "Rose", "Holdo", "Mon",
    "Peach", "Daisy", "Rosalina", "Pauline", "Toadette", "Birdo", "Samus", "Zelda", "Sheik", "Midna"
]

RECIPES = {
    "Hammer": {"Wood": 1, "Stone": 1},
    "Spear": {"Wood": 2, "Stone": 1},
    "Axe": {"Wood": 1, "Stone": 2},
    "Pickaxe": {"Wood": 2, "Stone": 2},
    "Campfire": {"Wood": 3, "Stone": 1},
    "Wall": {"Wood": 4},
    "Chest": {"Wood": 6},
    "Leather Bag": {"Leather": 2},
    "Shield": {"Wood": 2, "Leather": 1},
    "Bed": {"Wood": 4, "Leather": 2},
    "Clothes": {"Leather": 3}
}

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
        
        # Personality Vector (20 dimensions)
        personality_vector = {trait: np.random.random() for trait in PERSONALITY_TRAITS}
        
        self.attributes = AgentAttributes(name=name, 
                                          gender=gender,
                                          personality_vector=personality_vector,
                                          generation=1,
                                          curiosity=personality_vector["Curiosity"],
                                          honesty=personality_vector["Altruism"], # Approx
                                          aggression=personality_vector["Aggression"])
        self.state = AgentState()
        self.inventory: List[Dict] = []
        self.knowledge: List[str] = [] 
        self.equipped_items: List[Dict] = [] 
        
        # New Systems
        # New Systems
        self.memory: List[Memory] = [] # Structured memory
        self.plan: List[Dict] = [] # Current plan: [{'action': 'move', 'target': (x,y)}, ...]
        self.immediate_goal: str = "Idle"
        self.short_term_goal: str = "Survive"
        self.long_term_goal: str = "Thrive"
        
        # Initialize Values based on Personality
        self.attributes.values = {
            "Pacifism": self.attributes.personality_vector.get("Agreeableness", 0.5),
            "Preservation": self.attributes.personality_vector.get("Neuroticism", 0.5), # Fear drives preservation
            "Curiosity": self.attributes.personality_vector.get("Openness", 0.5),
            "Ambition": self.attributes.personality_vector.get("Conscientiousness", 0.5)
        }
        self.traits: List[str] = self._derive_traits(self.attributes.personality_vector)
        self.opinions: Dict[str, float] = {} # {agent_id: score (-1.0 to 1.0)}
        
        # Movement tracking
        self.last_x, self.last_y = x, y

    def _derive_traits(self, p: Dict[str, float]) -> List[str]:
        traits = []
        # Complex mappings
        if p["Survival"] > 0.7 and p["Caution"] > 0.6: traits.append("Survivor")
        if p["Social"] > 0.7 and p["Empathy"] > 0.7: traits.append("Empath")
        if p["Aggression"] > 0.7 and p["Impulsivity"] > 0.6: traits.append("Hot-headed")
        if p["Curiosity"] > 0.8 and p["Creativity"] > 0.7: traits.append("Inventor")
        if p["Bravery"] > 0.8 and p["Altruism"] > 0.6: traits.append("Heroic")
        if p["Logic"] > 0.8 and p["Patience"] > 0.7: traits.append("Strategist")
        if p["Greed"] > 0.8 and p["Selfishness"] > 0.7: traits.append("Hoarder")
        if p["Lust"] > 0.8 and p["Social"] > 0.6: traits.append("Flirtatious")
        if p["Laziness"] > 0.8: traits.append("Sloth")
        if p["Energy"] > 0.8: traits.append("Hyperactive")
        
        # Fallback basic traits if none complex found
        if not traits:
            if p["Social"] > 0.6: traits.append("Friendly")
            elif p["Social"] < 0.4: traits.append("Loner")
            if p["Curiosity"] > 0.6: traits.append("Curious")
            
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
            "immediate_goal": self.immediate_goal,
            "short_term_goal": self.short_term_goal,
            "long_term_goal": self.long_term_goal,
            "generation": self.attributes.generation,
            "opinions": self.opinions,
            "generation": self.attributes.generation,
            "opinions": self.opinions,
            "memory": [m.__dict__ for m in self.memory[-10:]], # Serialize memories
            "partner_id": self.attributes.partner_id,
            "friend_ids": self.attributes.friend_ids
        }

    def log_diary(self, entry: str):
        if not hasattr(self, 'diary'):
            self.diary = []
        self.diary.append(f"[Step {len(self.diary)}] {entry}")
        
    def add_memory(self, description: str, type: str = "event", location: tuple = None, impact: float = 0.0, entity_id: str = None):
        if location is None: location = (self.x, self.y)
        # Simple time approximation (len of memory)
        time = len(self.memory) 
        mem = Memory(type=type, description=description, location=location, time=time, emotional_impact=impact, related_entity_id=entity_id)
        self.memory.append(mem)
        # Keep memory size manageable
        if len(self.memory) > 100:
            self.memory.pop(0)

    def die(self, world, cause: str):
        world.log_event(f"Agent {self.attributes.name} died of {cause}.")
        if self.id in world.agents:
            del world.agents[self.id]

    def reproduce(self, partner, world):
        # Genetic Algorithm for offspring
        child_gender = np.random.choice(['male', 'female'])
        
        # Crossover Personality Vectors
        child_p_vector = {}
        for trait in PERSONALITY_TRAITS:
            # Randomly pick from p1 or p2, or average
            if np.random.random() < 0.4:
                val = self.attributes.personality_vector[trait]
            elif np.random.random() < 0.4:
                val = partner.attributes.personality_vector[trait]
            else:
                val = (self.attributes.personality_vector[trait] + partner.attributes.personality_vector[trait]) / 2.0
            
            # Mutation
            if np.random.random() < 0.1: # 10% mutation chance
                val += np.random.normal(0, 0.1)
            
            child_p_vector[trait] = float(np.clip(val, 0.0, 1.0))

        # Name generation
        child_name = np.random.choice(NAMES_MALE if child_gender == 'male' else NAMES_FEMALE)
        
        child = Agent(x=self.x, y=self.y, name=child_name, gender=child_gender)
        child.attributes.personality_vector = child_p_vector
        child.attributes.generation = max(self.attributes.generation, partner.attributes.generation) + 1
        
        # Update derived attributes
        child.attributes.curiosity = child_p_vector["Curiosity"]
        child.attributes.honesty = child_p_vector["Altruism"]
        child.attributes.aggression = child_p_vector["Aggression"]
        child.traits = child._derive_traits(child_p_vector)
        
        # Experience Transfer (Inherit some knowledge)
        if self.knowledge:
            child.knowledge.extend(np.random.choice(self.knowledge, size=min(len(self.knowledge), 2), replace=False))
        if partner.knowledge:
            child.knowledge.extend(np.random.choice(partner.knowledge, size=min(len(partner.knowledge), 2), replace=False))
        child.knowledge = list(set(child.knowledge)) # Deduplicate

            
    def formulate_plan(self, goal: str, world) -> bool:
        """
        Generates a plan based on the goal.
        Returns True if a plan was formed.
        """
        self.plan = []
        
        if goal == "Find Food":
            # 1. Check Memory
            best_mem = None
            for mem in self.memory:
                if "food" in mem.description.lower() or "fruit" in mem.description.lower():
                    best_mem = mem
                    # Use recent memories
                    if len(self.memory) - mem.time < 50: 
                        break
            
            if best_mem:
                self.plan.append({'action': 'move', 'target': best_mem.location, 'desc': f"Moving to remembered food at {best_mem.location}"})
                self.plan.append({'action': 'gather', 'target': None, 'desc': "Gathering food"})
                return True
            
            # 2. Explore (Fallback)
            # Pick a random point far away
            rx, ry = np.random.randint(0, world.width), np.random.randint(0, world.height)
            self.plan.append({'action': 'move', 'target': (rx, ry), 'desc': "Exploring for food"})
            return True

        elif goal == "Crafting":
            # Plan: Gather Wood -> Gather Stone -> Craft
            # Simplified: Just explore to find resources
            self.plan.append({'action': 'move', 'target': (np.random.randint(0, world.width), np.random.randint(0, world.height)), 'desc': "Looking for resources"})
            return True
            
        elif goal == "Socializing":
             # Find nearest agent memory?
             pass
             
        return False

    def execute_plan(self, world):
        if not self.plan:
            return

        step = self.plan[0]
        action = step['action']
        
        if action == 'move':
            tx, ty = step['target']
            dx = tx - self.x
            dy = ty - self.y
            
            if abs(dx) <= 1 and abs(dy) <= 1:
                # Arrived
                self.plan.pop(0)
                return
            
            # Move towards
            move_x = 1 if dx > 0 else -1 if dx < 0 else 0
            move_y = 1 if dy > 0 else -1 if dy < 0 else 0
            
            if not world.move_agent(self.id, move_x, move_y):
                 # Blocked? Try random
                 if np.random.random() < 0.5:
                    world.move_agent(self.id, np.random.randint(-1, 2), np.random.randint(-1, 2))
            
        elif action == 'gather':
            self.gather(world)
            self.plan.pop(0)

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
            
        # --- REACTIVE LAYER (Survival) ---
        # 0. Flee Predators
        nearby_carnivores = []
        for animal in world.animals:
            if animal.type == 'carnivore':
                dist = np.sqrt((self.x - animal.x)**2 + (self.y - animal.y)**2)
                if dist < 10:
                    nearby_carnivores.append((animal, dist))
        
        if nearby_carnivores:
            self.immediate_goal = "Fleeing Predator"
            self.plan = [] # Clear plan
            # Flee logic...
            nearest_carnivore = min(nearby_carnivores, key=lambda x: x[1])[0]
            dx = self.x - nearest_carnivore.x
            dy = self.y - nearest_carnivore.y
            move_x = 1 if dx > 0 else -1 if dx < 0 else np.random.choice([-1, 1])
            move_y = 1 if dy > 0 else -1 if dy < 0 else np.random.choice([-1, 1])
            world.move_agent(self.id, move_x, move_y)
            return

        # --- PROACTIVE LAYER (Planning) ---
        
        # 1. Determine Goal
        new_goal = "Idle"
        if self.state.hunger > 0.4:
            new_goal = "Find Food"
        elif np.random.random() < 0.1: # Occasional desire to craft
            new_goal = "Crafting"
        elif np.random.random() < 0.1:
            new_goal = "Socializing"
            
        # 2. Formulate Plan if Goal Changed or No Plan
        if new_goal != self.short_term_goal or not self.plan:
            self.short_term_goal = new_goal
            if new_goal != "Idle":
                self.formulate_plan(new_goal, world)
        
        # 3. Execute Plan
        if self.plan:
            self.immediate_goal = self.plan[0].get('desc', 'Acting')
            self.execute_plan(world)
            return
            
        # 4. Fallback (Idle/Wander)
        self.immediate_goal = "Wandering"
        move_x = np.random.randint(-1, 2)
        move_y = np.random.randint(-1, 2)
        
        # --- COHESION (Social Grouping) ---
        if self.attributes.friend_ids or self.attributes.partner_id:
            avg_x, avg_y = 0, 0
            count = 0
            
            if self.attributes.partner_id:
                p = world.agents.get(self.attributes.partner_id)
                if p:
                    avg_x += p.x
                    avg_y += p.y
                    count += 1
            
            for fid in self.attributes.friend_ids:
                f = world.agents.get(fid)
                if f:
                    avg_x += f.x
                    avg_y += f.y
                    count += 1
            
            if count > 0:
                avg_x /= count
                avg_y /= count
                
                # Bias movement towards group center
                if np.random.random() < 0.7: # 70% chance to follow group
                    if avg_x > self.x: move_x = 1
                    elif avg_x < self.x: move_x = -1
                    if avg_y > self.y: move_y = 1
                    elif avg_y < self.y: move_y = -1
        
        world.move_agent(self.id, move_x, move_y)
        
        # Creativity: Experimentation
        if self.attributes.personality_vector["Creativity"] > 0.7 and np.random.random() < 0.05:
            # Try to craft something random
            self.craft(world) # Craft method has random selection logic now
            self.log_diary("I felt creative and tried to make something.")

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
        
        # Sort by distance
        visible['agents'].sort(key=lambda x: x['dist'])
        
        # Animals
        for animal in world.animals:
            dist = np.sqrt((self.x - animal.x)**2 + (self.y - animal.y)**2)
            if dist < radius:
                prob = 1.0 - (dist / radius)
                if np.random.random() < prob:
                    visible['animals'].append(animal)
                    
        # Items
        for (ix, iy), items in world.items_grid.items():
            dist = np.sqrt((self.x - ix)**2 + (self.y - iy)**2)
            if dist < radius:
                prob = 1.0 - (dist / radius)
                if np.random.random() < prob:
                    for item in items:
                        visible['items'].append({'item': item, 'x': ix, 'y': iy})
        
        return visible

    def explore(self, world):
        # Random walk
        dx, dy = np.random.randint(-1, 2), np.random.randint(-1, 2)
        world.move_agent(self.id, dx, dy)

    def gather(self, world):
        # Try to pick up item at current location
        items = world.items_grid.get((self.x, self.y))
        if items:
            item = items.pop(0) # Take first item
            if not items:
                del world.items_grid[(self.x, self.y)]
            
            # Add to inventory
            found = False
            for slot in self.inventory:
                if slot['item']['id'] == item.id: # Same item type? No, ID is unique. Check Name/Type
                    # Simplified stacking by name for now
                    if slot['item']['name'] == item.name:
                        slot['count'] += 1
                        found = True
                        break
            
            if not found:
                self.inventory.append({'item': item.to_dict(), 'count': 1})
            
            self.log_diary(f"I gathered {item.name}.")
            self.add_memory(f"Found {item.name} at {self.x},{self.y}")

    def craft(self, world):
        # Check for possible recipes
        possible_recipes = []
        inventory_counts = {}
        for slot in self.inventory:
            name = slot['item']['name']
            inventory_counts[name] = inventory_counts.get(name, 0) + slot['count']
            
        for recipe_name, ingredients in RECIPES.items():
            can_craft = True
            for item_name, count in ingredients.items():
                if inventory_counts.get(item_name, 0) < count:
                    can_craft = False
                    break
            if can_craft:
                possible_recipes.append(recipe_name)
        
        if possible_recipes:
            # Pick one (Random for now, later based on needs)
            # Priority: Tools > Survival > Luxury
            # Simple heuristic: If we don't have it, craft it
            target_recipe = None
            
            # Check what we already have equipped or in inventory
            owned_items = [slot['item']['name'] for slot in self.inventory]
            
            for recipe in possible_recipes:
                if recipe not in owned_items:
                    target_recipe = recipe
                    break
            
            if not target_recipe:
                target_recipe = np.random.choice(possible_recipes)
            
            # Consume Ingredients
            ingredients = RECIPES[target_recipe]
            for item_name, count in ingredients.items():
                removed = 0
                # Iterate backwards to safely remove
                for i in range(len(self.inventory) - 1, -1, -1):
                    if self.inventory[i]['item']['name'] == item_name:
                        take = min(count - removed, self.inventory[i]['count'])
                        self.inventory[i]['count'] -= take
                        removed += take
                        if self.inventory[i]['count'] == 0:
                            self.inventory.pop(i)
                        if removed >= count:
                            break
                            
            # Create Item
            from ..env.item import Item
            import uuid
            
            # Determine tags based on type
            tags = ["craftable"]
            if target_recipe in ["Hammer", "Axe", "Pickaxe"]: tags.append("tool")
            elif target_recipe in ["Spear", "Shield"]: tags.append("weapon")
            elif target_recipe in ["Campfire", "Wall", "Chest", "Bed"]: tags.append("building")
            elif target_recipe in ["Leather Bag", "Clothes"]: tags.append("equipment")
            
            new_item = Item(id=f"{target_recipe.lower()}_{uuid.uuid4()}", name=target_recipe, weight=1.0, hardness=1.0, durability=1.0, tags=tags)
            self.inventory.append({'item': new_item.to_dict(), 'count': 1})
            
            self.log_diary(f"I crafted a {target_recipe}!")
            self.add_memory(f"Crafted {target_recipe} successfully.")
        else:
            self.log_diary("I wanted to craft but didn't have enough materials.")

    def socialize(self, world):
        # Find nearest agent
        nearest = None
        min_dist = float('inf')
        for other in world.agents.values():
            if other.id == self.id: continue
            dist = np.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
            if dist < min_dist:
                min_dist = dist
                nearest = other
        
        if nearest and min_dist < 5:
            self.communicate(nearest, world)
            
    def communicate(self, partner, world):
        # 1. Determine Opinion
        opinion = self.opinions.get(partner.id, 0.0)
        
        # 2. Decide Action based on Opinion + Personality
        # Friendly/Social agents are nicer even with neutral opinion
        base_attitude = self.attributes.personality_vector["Social"] - self.attributes.personality_vector["Aggression"]
        effective_opinion = opinion + base_attitude
        
        # Likeness Score (Personality Similarity)
        p1 = np.array(list(self.attributes.personality_vector.values()))
        p2 = np.array(list(partner.attributes.personality_vector.values()))
        # Euclidean distance, inverted and scaled. Max dist approx sqrt(20) ~ 4.5. 
        dist = np.linalg.norm(p1 - p2)
        likeness = max(0, (5.0 - dist) * 2.5) # Scale roughly 0-12.5
        
        # Relationship Logic
        if likeness > 10:
            # High compatibility
            if self.attributes.gender != partner.attributes.gender:
                # Potential Couple
                if not self.attributes.partner_id and not partner.attributes.partner_id:
                    if np.random.random() < 0.5: # Chance to pair
                        self.attributes.partner_id = partner.id
                        partner.attributes.partner_id = self.id
                        self.log_diary(f"I fell in love with {partner.attributes.name}!")
                        partner.log_diary(f"I fell in love with {self.attributes.name}!")
                
                # If partners, chance to reproduce
                if self.attributes.partner_id == partner.id:
                     if np.random.random() < 0.05: # 5% chance per interaction
                        self.reproduce(partner, world)
            
            else:
                # Potential Best Friend
                if partner.id not in self.attributes.friend_ids:
                    self.attributes.friend_ids.append(partner.id)
                    self.log_diary(f"{partner.attributes.name} is my new best friend.")
                if self.id not in partner.attributes.friend_ids:
                    partner.attributes.friend_ids.append(self.id)
        
        elif likeness > 6:
             # Friend
            if partner.id not in self.attributes.friend_ids:
                if np.random.random() < 0.2:
                    self.attributes.friend_ids.append(partner.id)
                    self.log_diary(f"I made friends with {partner.attributes.name}.")

        if effective_opinion > 0.2:
            # Positive: Help / Gift / Share Info
            if np.random.random() < 0.5:
                # Share Knowledge
                if self.knowledge:
                    info = np.random.choice(self.knowledge)
                    if info not in partner.knowledge:
                        partner.knowledge.append(info)
                        partner.log_diary(f"{self.attributes.name} told me about {info}.")
                        self.log_diary(f"I told {partner.attributes.name} about {info}.")
                        # Boost opinion (Tit for Tat)
                        partner.opinions[self.id] = partner.opinions.get(self.id, 0.0) + 0.1
        elif effective_opinion < -0.2:
            # Negative: Avoid / Trap
            self.log_diary(f"I avoided {partner.attributes.name}.")
            # Decrease opinion slightly
            self.opinions[partner.id] = self.opinions.get(partner.id, 0.0) - 0.05
        else:
            # Neutral
            self.log_diary(f"I chatted with {partner.attributes.name}.")
            # Small familiarity boost
            self.opinions[partner.id] = self.opinions.get(partner.id, 0.0) + 0.01

        # Ensure opinion exists
        if partner.id not in self.opinions:
             self.opinions[partner.id] = 0.0
             
        # Reciprocal update for partner (simplified)
        if self.id not in partner.opinions:
            partner.opinions[self.id] = 0.0

    def trade(self, partner, world) -> bool:
        # Placeholder
        return False
