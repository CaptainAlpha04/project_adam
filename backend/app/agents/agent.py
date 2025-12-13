from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import uuid
import numpy as np
from enum import Enum

class GameStrategy(Enum):
    ALWAYS_COOPERATE = "Always Cooperate"
    ALWAYS_DEFECT = "Always Defect"
    TIT_FOR_TAT = "Tit for Tat"
    GRIM_TRIGGER = "Grim Trigger"
    PAVLOV = "Pavlov" # Win-Stay, Lose-Shift
    RANDOM = "Random"
    
@dataclass
class AgentAttributes:
    name: str
    gender: str # 'male', 'female'
    personality_vector: Dict[str, float] # 20+ dimensions
    generation: int = 1
    partner_id: Optional[str] = None
    friend_ids: List[str] = None
    values: Dict[str, float] = None # Principles: {"Pacifism": 0.5, "Preservation": 0.8}
    strategy: str = "Tit for Tat"

    def __post_init__(self):
        if self.friend_ids is None:
            self.friend_ids = []
        if self.values is None:
            self.values = {}
        # Strategy is assigned by Agent based on personality during init usually
            
    curiosity: float = 0.5 
    honesty: float = 0.5
    metabolism: float = 0.5
    aggression: float = 0.1

@dataclass
class Soul:
    id: str
    memories: List['Memory']
    karma: float = 0.0
    past_lives: int = 0

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
    busy_until: int = 0
    last_interaction: Dict[str, Any] = field(default_factory=dict)


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

PERSONALITY_TRAITS = [
    "Curiosity", "Survival", "Social", "Aggression", "Loyalty", 
    "Independence", "Patience", "Impulsivity", "Creativity", "Logic", 
    "Empathy", "Selfishness", "Bravery", "Caution", "Energy", 
    "Laziness", "Lust", "Greed", "Altruism", "Resilience",
    "Optimism", "Pessimism", "Ambition", "Modesty", "Humor",
    "Seriousness", "Forgiveness", "Vengefulness", "Spirituality", "Skepticism"
]

class Agent:
    def __init__(self, x: int, y: int, name: str = None, gender: str = None, soul: Soul = None, birth_time: int = 0):
        self.id = str(uuid.uuid4())
        self.x = x
        self.y = y
        
        self.birth_time = birth_time
        
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

        # Samsara / Soul Logic
        if soul:
            self.soul_id = soul.id
            self.memory = soul.memories
            self.past_lives = soul.past_lives + 1
            # Karma influence?
            self.log_diary(f"I have awakened again. This is life #{self.past_lives}.")
        else:
            self.soul_id = str(uuid.uuid4())
            self.past_lives = 0
            
    def get_age(self, current_time: int) -> int:
        return current_time - self.birth_time

    def create_soul(self) -> Soul:
        """Extracts the soul from the dying agent."""
        # Filter memories? For now keep all or last N
        return Soul(
            id=self.soul_id,
            memories=self.memory[-50:], # Keep last 50 memories
            karma=0.0, # TODO: Calculate karma
            past_lives=self.past_lives
        )

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
            "memory": [m.__dict__ for m in self.memory[-10:]], # Serialize memories
            "partner_id": self.attributes.partner_id,
            "friend_ids": self.attributes.friend_ids
        }

    def get_resource_count(self, resource_name: str) -> int:
        """Helper to get count of a resource from inventory list."""
        for slot in self.inventory:
            if slot['item']['name'].lower() == resource_name.lower():
                return slot['count']
        return 0

    def add_resource(self, resource_name: str, amount: int = 1):
        """Helper to add a simple resource to inventory."""
        # Check if exists
        for slot in self.inventory:
            if slot['item']['name'].lower() == resource_name.lower():
                slot['count'] += amount
                if slot['count'] <= 0:
                    self.inventory.remove(slot)
                return
        
        # If not exists and adding positive amount
        if amount > 0:
            # Create dummy item for RL simplicity
            from ..env.item import Item
            import uuid
            new_item = Item(id=f"{resource_name}_{uuid.uuid4()}", name=resource_name.capitalize(), weight=1.0)
            self.inventory.append({'item': new_item.to_dict(), 'count': amount})

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
        
        # ADD TO WORLD
        if hasattr(world, 'agents'):
            world.agents[child.id] = child
            child.log_diary(f"I was born! Parents: {self.attributes.name} & {partner.attributes.name}")
            self.log_diary(f"I had a baby named {child.attributes.name}!")
            partner.log_diary(f"I had a baby named {child.attributes.name}!")

            
    def formulate_plan(self, goal: str, world) -> bool:
        """
        Generates a plan based on the goal.
        Returns True if a plan was formed.
        """
        self.plan = []
        
        if goal == "Find Food":
            # 0. Check Visible (Reactive)
            visible = self.perceive(world)
            for v_item in visible['items']:
                # Item object in visible list, not dict
                if "consumable" in v_item['item'].tags:
                     self.plan.append({'action': 'move', 'target': (v_item['x'], v_item['y']), 'desc': f"Moving to visible {v_item['item'].name}"})
                     self.plan.append({'action': 'gather', 'target': None, 'desc': "Gathering food"})
                     return True
        
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
            
            # 2. Explore Resource Zones (Smart Exploration)
            # Try to find a Grass(2) or Forest(3) tile to explore
            found_zone = False
            for _ in range(5):
                rx, ry = np.random.randint(0, world.width), np.random.randint(0, world.height)
                # This cheats slightly by knowing world terrain, but represents "Knowledge of Biomes"
                tile_type = world.terrain_grid[ry][rx]
                if tile_type in [2, 3]: # Grass or Forest
                    self.plan.append({'action': 'move', 'target': (rx, ry), 'desc': "Searching foraging grounds"})
                    found_zone = True
                    break
            
            if not found_zone:
                rx, ry = np.random.randint(0, world.width), np.random.randint(0, world.height)
                self.plan.append({'action': 'move', 'target': (rx, ry), 'desc': "Exploring for food"})
            return True

        elif goal == "Crafting":
            # Simplified: Just explore to find resources
            self.plan.append({'action': 'move', 'target': (np.random.randint(0, world.width), np.random.randint(0, world.height)), 'desc': "Looking for resources"})
            return True

        elif goal == "Gather Resources":
            # Hoarding: Go find items even if not hungry
            self.plan.append({'action': 'move', 'target': (np.random.randint(0, world.width), np.random.randint(0, world.height)), 'desc': "Hoarding resources"})
            self.plan.append({'action': 'gather', 'target': None, 'desc': "Gathering resources"})
            return True
            
        elif goal == "Socializing":
             # Find nearest visible agent
             visible = self.perceive(world)
             if visible['agents']:
                 target_agent = visible['agents'][0]['agent'] # Nearest
                 self.plan.append({'action': 'move', 'target': (target_agent.x, target_agent.y), 'desc': f"Visiting {target_agent.attributes.name}"})
                 self.plan.append({'action': 'socialize', 'target': target_agent.id, 'desc': f"Socializing with {target_agent.attributes.name}"})
                 return True
             else:
                 # No one visible? Wander to find someone
                 rx, ry = np.random.randint(0, world.width), np.random.randint(0, world.height)
                 self.plan.append({'action': 'move', 'target': (rx, ry), 'desc': "Searching for friends"})
                 return True
             
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

        elif action == 'socialize':
            # Logic: If close enough, communicate. If not, plan fails (or we just tried).
            self.socialize(world)
            self.plan.pop(0)

    def act(self, action_idx: int, world):
        """
        Executes an action.
        Prioritizes survival > social > exploration.
        """
        # Check if busy (Face-to-Face communication)

            
        # Update Age
        age = self.get_age(world.time_step)
        
        # Entropy Ticker (Hunger Decay)
        self.state.hunger += 0.001

        # SAFETY NET: Auto-eat if getting very hungry
        if self.state.hunger > 0.7:
             self.eat_from_inventory() # Takes no time, just consumes item

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
        # 0. Flee Predators (Overrides EVERYTHING, even social locks)
        nearby_carnivores = []
        for animal in world.animals:
            if animal.type == 'carnivore':
                dist = np.sqrt((self.x - animal.x)**2 + (self.y - animal.y)**2)
                if dist < 10:
                    nearby_carnivores.append((animal, dist))
        
        if nearby_carnivores:
            self.immediate_goal = "Fleeing Predator"
            # Break Social Lock if exists
            if self.state.busy_until > world.time_step:
                self.log_diary("I broke off the chat to run for my life!")
                self.state.busy_until = 0
                
            self.plan = [] # Clear plan
            # Flee logic...
            nearest_carnivore = min(nearby_carnivores, key=lambda x: x[1])[0]
            dx = self.x - nearest_carnivore.x
            dy = self.y - nearest_carnivore.y
            move_x = 1 if dx > 0 else -1 if dx < 0 else np.random.choice([-1, 1])
            move_y = 1 if dy > 0 else -1 if dy < 0 else np.random.choice([-1, 1])
            world.move_agent(self.id, move_x, move_y)
            return

        # Check if busy (Face-to-Face communication)
        if world.time_step < self.state.busy_until:
            # HUNGER OVERRIDE: If starving, break social lock
            if self.state.hunger > 0.6: # Relaxed slightly from 0.8 to be safer
                self.log_diary("I'm too hungry to chat!")
                self.state.busy_until = 0 # Break lock
                self.social_cooldown = world.time_step + 20 # Don't chat for 20 ticks
                # Fall through to allow acting (finding food)
            else:
                # SOCIAL MULTITASKING: Eat or Gather while chatting
                # 1. Eat if hungry and have food
                if self.state.hunger > 0.5:
                     self.eat_from_inventory()
                
                # 2. Gather if standing on item
                if world.items_grid.get((self.x, self.y)):
                     self.gather(world)
                     # Optional: Log sharing?
                     if hasattr(self.state, 'last_interaction') and self.state.last_interaction.get('type') == 'love':
                         self.log_diary("We gathered resources together <3")
                         
                return # Still busy (don't move)

        # --- PROACTIVE LAYER (Planning) ---
        
        # 1. Determine Goal
        new_goal = "Idle"
        if self.state.hunger > 0.4: # Lowered from 0.6 to be proactive
            new_goal = "Find Food"
        elif np.random.random() < 0.4:
            new_goal = "Socializing"
        elif np.random.random() < 0.2: # Increased crafting/hoarding chance
            if np.random.random() < 0.5:
                new_goal = "Crafting"
            else:
                new_goal = "Gather Resources" # Hoarding
            
        # Opportunistic Socializing: If someone is VERY close, chat!
        if new_goal == "Idle":
            nearby = [a for a in perceived['agents'] if a['dist'] < 3]
            if nearby:
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
            
        # 4. Fallback (Persistent Wandering)
        self.immediate_goal = "Wandering"
        
        # Initialize or update wandering target
        if not hasattr(self, 'wander_target') or self.has_reached_target(self.wander_target):
             # Pick new distant target
             # Biased towards Green zones if hungry?
             while True:
                 wx, wy = np.random.randint(0, world.width), np.random.randint(0, world.height)
                 if np.sqrt((self.x-wx)**2 + (self.y-wy)**2) > 20: # Must be far
                     self.wander_target = (wx, wy)
                     break
        
        # Move towards wander target
        dx = self.wander_target[0] - self.x
        dy = self.wander_target[1] - self.y
        move_x = 1 if dx > 0 else -1 if dx < 0 else 0
        move_y = 1 if dy > 0 else -1 if dy < 0 else 0
        
        # Add some noise (10% chance to deviate)
        if np.random.random() < 0.1:
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
                
                # Gentle Cohesion (Vector Bias) instead of Override
                # If wandering, slightly pull towards group
                if self.immediate_goal == "Wandering":
                     bias_x = 0
                     bias_y = 0
                     if avg_x > self.x + 5: bias_x = 1
                     elif avg_x < self.x - 5: bias_x = -1
                     
                     if avg_y > self.y + 5: bias_y = 1
                     elif avg_y < self.y - 5: bias_y = -1
                     
                     # 30% chance to apply bias if moving away
                     if np.random.random() < 0.3:
                         if bias_x != 0: move_x = bias_x
                         if bias_y != 0: move_y = bias_y
        
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
                # Guaranteed vision if close, probabilistic if far
                prob = 1.0 if dist < 10 else 1.0 - (dist / radius)
                if np.random.random() < prob:
                    for item in items:
                        visible['items'].append({'item': item, 'x': ix, 'y': iy})
        
        return visible
    
    def has_reached_target(self, target):
        dist = np.sqrt((self.x - target[0])**2 + (self.y - target[1])**2)
        return dist < 2.0

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

    def eat_from_inventory(self):
        """Consumes food from inventory."""
        for i, slot in enumerate(self.inventory):
            if "consumable" in slot['item']['tags']:
                slot['count'] -= 1
                self.state.hunger = max(0, self.state.hunger - 0.5) # Eat restores 0.5 hunger
                self.log_diary(f"I ate a {slot['item']['name']} from my bag.")
                self.add_memory(f"Ate {slot['item']['name']}", type="survival", impact=0.2)
                
                if slot['count'] <= 0:
                    self.inventory.pop(i)
                return True
        return False

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
        # Check Cooldown (Survival Priority)
        if getattr(self, 'social_cooldown', 0) > world.time_step:
            return # I need to eat/run, no chatting!
            
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
        
        # --- PATH A: LOVE & REPRODUCTION ---
        if likeness > 10 and self.attributes.gender != partner.attributes.gender:
            # Potential Match
            if not self.attributes.partner_id and not partner.attributes.partner_id:
                 # Romance Bloom
                 if np.random.random() < 0.6:
                    self.attributes.partner_id = partner.id
                    partner.attributes.partner_id = self.id
                    self.log_diary(f"I fell deeply in love with {partner.attributes.name}!")
                    partner.log_diary(f"I found my soulmate in {self.attributes.name}!")
                    partner.log_diary(f"I found my soulmate in {self.attributes.name}!")
                    if hasattr(self.state, 'last_interaction'): self.state.last_interaction["type"] = "love"
                    
                    # Love Lock (Long)
                    self.state.busy_until = world.time_step + 20
                    partner.state.busy_until = world.time_step + 20

            if self.attributes.partner_id == partner.id:
                # Existing Partners: Reproduce
                if np.random.random() < 0.2: # 20% chance if they meet
                    if hasattr(self.state, 'last_interaction'): self.state.last_interaction["type"] = "reproduce"
                    self.reproduce(partner, world)
                    return # Busy making baby
        
        elif likeness > 6:
             # Friend
            if partner.id not in self.attributes.friend_ids:
                if np.random.random() < 0.2:
                    self.attributes.friend_ids.append(partner.id)
                    self.log_diary(f"I made friends with {partner.attributes.name}.")

        # --- PATH B: HATE & MURDER ---
        # Trigger: Hated Opinion + High Aggression + Low Empathy
        if effective_opinion < -0.8:
            if self.attributes.aggression > 0.7 and self.attributes.personality_vector["Empathy"] < 0.3:
                # Murder Logic
                if np.random.random() < 0.1: # 10% chance to act on impulse
                    self.log_diary(f"I couldn't take it anymore. I attacked {partner.attributes.name}!")
                    if hasattr(self.state, 'last_interaction'): self.state.last_interaction["type"] = "combat"
                    
                    # Combat Lock (Medium)
                    self.state.busy_until = world.time_step + 15
                    partner.state.busy_until = world.time_step + 15
                    
                    # Simple Combat logic
                    my_score = self.attributes.aggression * self.state.health
                    their_score = partner.attributes.aggression * partner.state.health
                    
                    if my_score > their_score:
                        self.log_diary(f"I killed {partner.attributes.name}.")
                        partner.die(world, f"murdered by {self.attributes.name}")
                        self.attributes.personality_vector["Aggression"] = min(1.0, self.attributes.personality_vector["Aggression"] + 0.1)
                        # Remove from opinions if dead? Or keep memory? Keep memory.
                        return
                    else:
                        self.log_diary(f"I tried to kill {partner.attributes.name} but failed.")
                        partner.log_diary(f"{self.attributes.name} tried to kill me!")
                        partner.opinions[self.id] = -1.0 # Eternal Enemy
                        if hasattr(self.state, 'last_interaction'): self.state.last_interaction["type"] = "combat"

        # --- PATH C: NORMAL SOCIAL ---
        if effective_opinion > 0.2:
            # Positive: Help / Gift / Share Info
            # Locked Duration depends on closeness
            duration = 5
            if effective_opinion > 0.6: duration = 15 # Close friends talk longer
            
            self.state.busy_until = world.time_step + duration
            partner.state.busy_until = world.time_step + duration

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
            if hasattr(self.state, 'last_interaction'): self.state.last_interaction["type"] = "conflict"
            # No lock for avoidance
        else:
            # Neutral
            self.log_diary(f"I chatted with {partner.attributes.name}.")
            # Small familiarity boost
            self.opinions[partner.id] = self.opinions.get(partner.id, 0.0) + 0.01
            # Short Lock
            self.state.busy_until = world.time_step + 4
            partner.state.busy_until = world.time_step + 4

        # Ensure opinion exists
        if partner.id not in self.opinions:
             self.opinions[partner.id] = 0.0
             
        # Reciprocal update for partner (simplified)
        if self.id not in partner.opinions:
            partner.opinions[self.id] = 0.0
            
        # LOCK AGENTS (Face-to-Face Waiting)
        # If any significant interaction happened (Love, Fight, Reproduce, or just Chat)
        # Set busy_until for both agents to freeze them
        # --- PATH C: NEUTRAL / TRADE ---
        # Casual Chat
        # The busy_until logic is now handled within each path (Love, Friend, Hate, Positive, Negative, Neutral)
        # This ensures specific durations for specific interactions.
        
        # Trade Check (Can happen during any non-hostile interaction)
        if effective_opinion >= -0.2: # Don't trade with someone you hate
            self.trade(partner, world)

        # Update Opinions
        self.opinions[partner.id] = np.clip(effective_opinion, -1.0, 1.0)
        if hasattr(self.state, 'last_interaction'): self.state.last_interaction["partner"] = partner.id

    def trade(self, partner, world) -> bool:
        """
        Simple Trade Logic: Give surplus items to friends/needs.
        """
        # 1. Identify Needs
        my_needs = []
        if self.state.hunger > 0.4: my_needs.append("food")
        
        partner_needs = []
        if partner.state.hunger > 0.4: partner_needs.append("food")
        
        # 2. Check Inventory (Surplus)
        for i, slot in enumerate(self.inventory):
            item = slot['item']
            count = slot['count']
            
            # Give Food if partner needs it and we have enough
            if "food" in partner_needs and "consumable" in item["tags"]:
                 if count > 1 or (self.state.hunger < 0.2 and count >= 1):
                     # GIVE ITEM
                     slot['count'] -= 1
                     if slot['count'] <= 0: self.inventory.pop(i)
                     
                     # Add to partner
                     partner.inventory.append({'item': item, 'count': 1})
                     
                     self.log_diary(f"I gave {item['name']} to {partner.attributes.name}.")
                     partner.log_diary(f"{self.attributes.name} gave me {item['name']}! Thanks!")
                     
                     # Boost Opinion
                     partner.opinions[self.id] = min(1.0, partner.opinions.get(self.id, 0) + 0.2)
                     return True
        
        return False

    def get_observation(self, world):
        """
        Constructs the observation vector for the RL brain.
        Must match the observation space in AdamBaseEnv.
        """
        # Construct 5x5 grid observation (Simplified for now as per envs.py)
        # Vision: Just relative vector to nearest food + internal state
        
        # Find nearest food
        nearest_dist = float('inf')
        fx, fy = 0, 0
        
        # Note: World in main sim might use different food structure than TestWorld
        # TestWorld uses set of tuples. Main World uses list of objects or similar?
        # Let's assume TestWorld structure for now or check.
        # Main World does NOT have food_grid set. It has items? Or resource spawning?
        # Main World has 'respawn_resources' but we didn't check how it stores food.
        # Checking envs.py: self.world.food_grid.add((fx, fy))
        
        # We need to support both.
        # If world has food_grid (TestWorld), use it.
        # If world is Main World, we need to find "Food" items.
        
        food_locations = []
        if hasattr(world, 'food_grid') and world.food_grid:
            food_locations = list(world.food_grid)
        elif hasattr(world, 'animals'):
             # Treat animals as food for the "Find Food" brain
             food_locations = [(a.x, a.y) for a in world.animals]
             
        for (fdx, fdy) in food_locations:
            dist = abs(fdx - self.x) + abs(fdy - self.y)
            if dist < nearest_dist:
                nearest_dist = dist
                fx, fy = fdx, fdy
        
        # Normalize relative position
        # Width/Height might be on world
        width = getattr(world, 'width', 200)
        height = getattr(world, 'height', 200)
        
        rel_x = (fx - self.x) / width
        rel_y = (fy - self.y) / height
        
        # Placeholder for full grid
        obs = np.zeros(77, dtype=np.float32)
        obs[0] = rel_x
        obs[1] = rel_y
        obs[2] = self.state.hunger
        
        return obs

    def load_brain(self, path: str):
        """Loads a trained PPO model as the agent's brain."""
        try:
            from stable_baselines3 import PPO
            self.brain = PPO.load(path)
            print(f"Agent {self.attributes.name} loaded brain from {path}")
        except Exception as e:
            print(f"Failed to load brain for agent {self.attributes.name}: {e}")
            self.brain = None
            
    def act_smart(self, world):
        """Uses the RL brain to decide action."""
        if hasattr(self, 'brain') and self.brain:
            obs = self.get_observation(world)
            action, _ = self.brain.predict(obs)
            return int(action)
        return None

    def _assign_strategy(self, p: Dict[str, float]) -> GameStrategy:
        # Map personality to Game Theory Strategy
        # High Aggression -> Defect
        if p["Aggression"] > 0.8 or p["Selfishness"] > 0.8:
            return GameStrategy.ALWAYS_DEFECT
        
        # High Altruism + Naivety (Low Skepticism) -> Always Cooperate
        if p["Altruism"] > 0.7 and p.get("Skepticism", 0.5) < 0.3:
            return GameStrategy.ALWAYS_COOPERATE
            
        # Vengeful -> Grim Trigger
        if p.get("Vengefulness", 0.5) > 0.8:
            return GameStrategy.GRIM_TRIGGER
            
        # Logical/Adaptive -> Pavlov or TitForTat
        if p.get("Logic", 0.5) > 0.7:
             if np.random.random() < 0.5: return GameStrategy.PAVLOV
             else: return GameStrategy.TIT_FOR_TAT
             
        # Default -> Tit For Tat (Robust)
        return GameStrategy.TIT_FOR_TAT
