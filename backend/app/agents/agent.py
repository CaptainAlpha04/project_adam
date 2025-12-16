from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import uuid
import numpy as np
from enum import Enum

# --- Enums & Constants ---

class GameStrategy(Enum):
    ALWAYS_COOPERATE = "Always Cooperate"
    ALWAYS_DEFECT = "Always Defect"
    TIT_FOR_TAT = "Tit for Tat"
    TIT_FOR_TWO_TATS = "Tit for Two Tats"
    GRIM_TRIGGER = "Grim Trigger"
    PAVLOV = "Pavlov" # Win-Stay, Lose-Switch
    RANDOM = "Random"
    UNFORGIVING = "Unforgiving" # Same as Grim Trigger but stricter naming
    PEACEMAKER = "Peacemaker" # Tit for Tat but periodically forgives
    BULLY = "Bully" # Defect unless punished twice

NAMES_MALE = [
    "Adam", "Bob", "Charlie", "David", "Ethan", "Frank", "George", "Henry", "Isaac", "Jack",
    "Liam", "Noah", "Oliver", "Elijah", "James", "William", "Benjamin", "Lucas", "Mason", "Logan",
    "Alexander", "Sebastian", "Jack", "Aiden", "Owen", "Samuel", "Matthew", "Joseph", "Levi", "Mateo"
]

NAMES_FEMALE = [
    "Alice", "Bella", "Clara", "Diana", "Eve", "Fiona", "Grace", "Hannah", "Ivy", "Julia",
    "Olivia", "Emma", "Ava", "Charlotte", "Sophia", "Amelia", "Isabella", "Mia", "Evelyn", "Harper",
    "Camila", "Gianna", "Abigail", "Luna", "Ella", "Elizabeth", "Sofia", "Emily", "Avery", "Mila"
]

PERSONALITY_TRAITS = [
    "Curiosity", "Survival", "Social", "Aggression", "Loyalty", 
    "Independence", "Patience", "Impulsivity", "Creativity", "Logic", 
    "Empathy", "Selfishness", "Bravery", "Caution", "Energy", 
    "Laziness", "Lust", "Greed", "Altruism", "Resilience",
    "Optimism", "Pessimism", "Ambition", "Modesty", "Humor",
    "Seriousness", "Forgiveness", "Vengefulness", "Spirituality", "Skepticism"
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

# --- Data Structures ---

@dataclass
class Memory:
    type: str # 'event', 'location', 'social', 'survival'
    description: str
    location: tuple # (x, y)
    time: int
    emotional_impact: float # -1.0 to 1.0
    related_entity_id: Optional[str] = None

@dataclass
class Soul:
    """The persistent spiritual kernel that transmigrates."""
    id: str
    memories: List[Memory]
    karma: float = 0.0
    past_lives: int = 0
    wisdom_score: float = 0.0

@dataclass
class AgentAttributes:
    name: str
    gender: str
    personality_vector: Dict[str, float]
    generation: int = 1
    partner_id: Optional[str] = None
    friend_ids: List[str] = field(default_factory=list)
    values: Dict[str, float] = field(default_factory=dict)
    
    # Social Hierarchy
    leader_id: Optional[str] = None
    followers: List[str] = field(default_factory=list)
    ranking: float = 0.0 # Derived from influence
    candidate_tribe_id: Optional[str] = None # For joining logic
    tribe_id: Optional[str] = None
    
    # Social Hierarchy
    leader_id: Optional[str] = None
    followers: List[str] = field(default_factory=list)
    ranking: float = 0.0 # Derived from influence
    tribe_goal: str = "wander" # Deprecated, use Tribe.goal
    
    # Strategy
    strategy: str = "Tit for Tat"
    
    # Derived shortcuts
    curiosity: float = 0.5 
    honesty: float = 0.5
    honesty: float = 0.5
    aggression: float = 0.1
    is_prophet: bool = False

@dataclass
class AgentState:
    health: float = 1.0
    happiness: float = 0.5
    experience: float = 0.0
    busy_until: int = 0
    last_interaction: Dict[str, Any] = field(default_factory=dict)
    
    # Social State
    social_lock_target: Optional[str] = None
    social_lock_steps: int = 0
    
    age_steps: int = 0
    momentum_dir: tuple = (0, 0) # (dx, dy) for smoother wandering

# --- THE TRI-PARTITE PROTOCOL ---

class Nafs:
    """
    The Base Layer (The Reptile).
    Responsible for Biological Survival, Hunger, Pain, and Reactive Defense.
    """
    def __init__(self, agent):
        self.agent = agent
        self.hunger: float = 0.0 # 0.0 Full -> 1.0 Starving
        self.energy: float = 1.0 # 1.0 Rested -> 0.0 Exhausted
        self.pain: float = 0.0
        self.lust: float = 0.0
        
    def update(self, world):
        # Biological Decay
        self.hunger += 0.002
        self.energy -= 0.0002
        if self.agent.state.health > 0.8:
            self.lust += 0.005 # Grows faster than hunger if healthy
        
        # Health Impact
        if self.hunger > 0.8:
            drain = 0.01 if self.hunger <= 0.95 else 0.05
            self.agent.state.health -= drain
            if np.random.random() < 0.05:
                self.agent.log_diary("My stomach screams in agony.")

    def check_survival_instinct(self, world) -> Optional[Dict]:
        """
        Overrides higher functions if immediate survival is threatened.
        Returns an Action Plan if override is necessary.
        """
        # 1. Flee Predators (Immediate)
        nearby_threats = [a for a in world.animals if a.type == 'carnivore' and self.agent.distance_to(a) < 15]
        if nearby_threats:
            self.agent.log_diary("NAFS TAKEOVER: Fleeing predator!")
            return {'action': 'flee', 'target': nearby_threats[0]}

        # 2. Starvation Panic
        if self.hunger > 0.9:
            # Check for food in inventory
            if self.agent.eat_from_inventory():
                return None # Crisis averted
            
            # Panic Search
            self.agent.log_diary("NAFS TAKEOVER: Starvation Imminent!")
            return {'action': 'panic_search', 'target': None}
            
        return None

class Qalb:
    """
    The Middle Layer (The Heart/Ego).
    Responsible for Society, Emotion, Mediation, and Daily Logic.
    """
    def __init__(self, agent):
        self.agent = agent
        self.social: float = 1.0 # 1.0 Connected -> 0.0 Lonely
        self.fun: float = 1.0    # 1.0 Entertained -> 0.0 Bored
        self.emotional_state: str = "Neutral"
        self.opinions: Dict[str, float] = {} # agent_id -> -1.0 to 1.0
        self.social_memory: Dict[str, str] = {} # agent_id -> 'cooperate' or 'defect' (Last move they made against me)
        self.history: Dict[str, List[str]] = {} # agent_id -> List of past moves for complex strategies
        self.social_cooldowns: Dict[str, int] = {} # agent_id -> timestamp when cooldown expires
        
        # Social goals
        
        # Social goals
        self.current_social_target: Optional[str] = None
        self.brain = None # RL Model

    def load_brain(self, path):
        try:
            from stable_baselines3 import PPO
            self.brain = PPO.load(path)
            print(f"Agent {self.agent.attributes.name} loaded brain from {path}")
        except Exception as e:
            print(f"Failed to load brain: {e}")

    def update(self, world):
        self.social -= 0.0005
        self.fun -= 0.0005
        
        # Mood Calculation
        if self.agent.state.happiness > 0.7: self.emotional_state = "Happy"
        elif self.agent.state.happiness < 0.3: self.emotional_state = "Depressed"
        elif self.social < 0.2: self.emotional_state = "Lonely"
        else: self.emotional_state = "Neutral"

    def propose_action(self, world) -> Dict:
        """
        Calculates Desires based on Internal State and Personality.
        This is not a hardcoded utility function. It is a 'Feeling' generator.
        """
        # DEBUG LOG
        # print(f"Agent {self.agent.id[:4]} Proposing Action...")
        # 0. SOCIAL LOCK - REMOVED (Handled in Multitasking Act Loop)
        # But we should suppress "Socialize" desire if already locked to prevent switching targets?
        # Or keep it to maintain lock? 
        # Actually, if we are multitasking, we don't need to "propose" continue_social as the MAIN action.
        # We want to propose "Work" or "Gather" while social runs in background.
        
        # 0. BRAIN OVERRIDE (The Intuition)
        # if self.brain:
            # self.agent.log_diary("DEBUG: Brain Override")
            # obs = self.agent.get_observation(world)
            # action_idx, _ = self.brain.predict(obs)
            # action_idx = int(action_idx)
            # if action_idx == 0: return {'action': 'wait', 'desc': 'Thinking...'}
            # if action_idx == 1: return {'action': 'step_y', 'val': -1, 'desc': 'Moving Up'}
            # if action_idx == 2: return {'action': 'step_y', 'val': 1, 'desc': 'Moving Down'}
            # if action_idx == 3: return {'action': 'step_x', 'val': -1, 'desc': 'Moving Left'}
            # if action_idx == 4: return {'action': 'step_x', 'val': 1, 'desc': 'Moving Right'}
            # if action_idx == 5: return {'action': 'interact', 'desc': 'interacting'}

        p = self.agent.attributes.personality_vector

        # --- THE DESIRE SYSTEM ---
        # Instead of 'Utility', we use 'Desire Strength' (0.0 to 1.0)
        # Desires are emergent from Needs + Personality
        
        desires = {}

        # 1. Desire for Sustenance (Nafs + Conscientiousness)
        # "I feel hunger."
        # Logic: Hunger * (1 + 0.5 * Survival_Instinct)
        # Plan Ahead: If Conscientious, add weight to future hunger prediction
        predicted_hunger = self.agent.nafs.hunger + (0.1 if p.get("Conscientiousness", 0.5) > 0.6 else 0.0)
        # Amplified Hunger to ensure they eat before starving
        desires["Eat"] = min(1.0, predicted_hunger * (2.0 + p["Survival"]))

        # 2. Desire for Connection (Social + Extroversion + Boredom)
        # "I feel lonely OR bored."
        
        extroversion = p["Social"]
        loneliness = 1.0 - self.social
        boredom = 1.0 - self.fun
        
        # Base Desire
        if extroversion > 0.7:
             desire_social = (loneliness ** 0.5) + (boredom * 0.5)
        else:
             desire_social = (loneliness ** 1.5) + (boredom * 0.3) # Increased from 2.0/0.2 to be more active
        
        # Amplification: If really lonely, it should be painful
        if loneliness > 0.8: desire_social += 0.2
        
        # OPPORTUNITY BONUS
        # If I see someone close, it's "Cheap" to socialize.
        nearest_agent_dist = 999.0
        for other in world.agents.values():
             if other.id == self.agent.id: continue
             d = self.agent.distance_to(other)
             if d < nearest_agent_dist: nearest_agent_dist = d
        
        if nearest_agent_dist < 5.0:
             desire_social += 0.7 # Interaction is irresistible when close
             # Work dampening applied after work calculation
        
        desires["Socialize"] = min(1.0, desire_social)
        
        # MULTITASKING: If already locked, suppress desire to socialize so we can do other things (Work/Eat)
        # The social loop runs in the background (Agent.act -> process_social_loop)
        if self.agent.state.social_lock_target and self.agent.state.social_lock_steps > 0:
            desires["Socialize"] = 0.0
        
        # 3. Desire for Lust (The Bridge)
        # Driven by Nafs.lust + Libido (Lust trait)
        libido = p["Lust"]
        lust_drive = self.agent.nafs.lust * (1.0 + libido)
        desires["Mating"] = min(1.0, lust_drive)

        # 4. Desire for Curiosity (Strangers)
        # If I see a stranger (someone I have no opinion of), I want to know them.
        # This solves "First Contact"
        
        # Scan immediate vicinity (Vision)
        unknown_nearby = False
        candidates = [] # For action targeting
        
        # We need to know who is nearby to check opinions
        # Using World Access cheat for Efficiency (or could use spatial_memory['agent'])
        # Let's use the 'candidates' from vision scan in propose_action? No, that's inside socialize.
        # We need a quick check here.
        
        for other in world.agents.values():
            if other.id == self.agent.id: continue
            dist = self.agent.distance_to(other)
            if dist < 15: # Visual range
                 if other.id not in self.agent.qalb.opinions:
                     unknown_nearby = True
                     candidates.append(other)

        if unknown_nearby:
            # Curiosity Bonus
            curiosity_drive = p["Curiosity"]
            desires["Exploration"] = 0.5 + (curiosity_drive * 0.5) # Minimum 0.5 interest in strangers
            # If High Extroversion + Curiosity, it's irrelevant of hunger almost
            if p["Social"] > 0.6: desires["Exploration"] += 0.3
            
        else:
            desires["Exploration"] = p["Curiosity"] * 0.3 # Just wandering check
        
        # 5. Desire for Rest (Energy) - DISABLED
        # desires["Sleep"] = (1.0 - self.agent.nafs.energy) ** 1.5
        desires["Sleep"] = 0.0

        # 6. Desire for Achievement (Work)
        # DAMPENER: If Inventory is full, stop working!
        inventory_count = sum([s['count'] for s in self.agent.inventory])
        saturation = min(1.0, inventory_count / 20.0) 
        
        if self.agent.nafs.energy > 0.6:
            base_work_desire = p["Creativity"] * 0.8
            desires["Work"] = base_work_desire * (1.0 - saturation)
        else:
            desires["Work"] = 0.0
            
        # DISTRACTION: If social opportunity is high, work less
        # DISTRACTION: If social opportunity is high, work less
        # MULTITASKING FIX: We want them to work even if friends are near.
        # if nearest_agent_dist < 5.0:
        #     desires["Work"] *= 0.2

        # --- ARBITRATION ---
        
        dominant_desire = max(desires, key=desires.get)
        intensity = desires[dominant_desire]
        
        # DEBUG
        if intensity > 0.0:
            self.agent.log_diary(f"DEBUG: Desire {dominant_desire} ({intensity:.2f})")
            pass

        # REPRODUCTION (Opportunistic Override) - DISABLED
        # User wants reproduction only on specific milestones (multiples of 60 opinion)
        # if self.agent.state.happiness > 0.6 and self.agent.attributes.partner_id:
        #      if self.agent.nafs.energy > 0.4:
        #          return {'action': 'reproduce', 'desc': "Expanding the bloodline."}

        # ACTION MAPPING
        if dominant_desire == "Eat":
            if intensity > 0.2: 
                return {'action': 'find_resource', 'resource': 'consumable', 'desc': "Seeking sustenance."}
        
        elif dominant_desire == "Mating":
            # Seek ANY partner, preferably opposite gender, or just socialize aggressively
            # For now, map to 'socialize' but with high priority
            if intensity > 0.4:
                 return {'action': 'socialize', 'desc': "Driven by biological urge."}
                 
        elif dominant_desire == "Exploration":
            # If stranger nearby, go towards them
            if unknown_nearby:
                 return {'action': 'socialize', 'desc': "Investigating stranger."}
            else:
                 return {'action': 'wander', 'desc': "Exploring the unknown."}

        elif dominant_desire == "Sleep":
            if intensity > 0.6: 
                return {'action': 'sleep', 'desc': "Resting weary bones."}
                
        elif dominant_desire == "Socialize":
            if intensity > 0.3:
                return {'action': 'socialize', 'desc': "Seeking companionship."}
                
        elif dominant_desire == "Work":
             return {'action': 'gather_materials', 'resource': 'material', 'desc': "Building legacy."}
        
        # Default
        return {'action': 'wander', 'desc': "Contemplating existence."}

class Ruh:
    """
    The High Layer (The Spirit).
    Responsible for Life Goals, Wisdom, Karma, and Override.
    """
    def __init__(self, agent, soul: Optional[Soul] = None):
        self.agent = agent
        self.soul = soul if soul else Soul(id=str(uuid.uuid4()), memories=[])
        self.life_goal: str = "Survival" # Default
        self.wisdom: float = self.soul.wisdom_score
        
        self.determine_life_goal()

    def determine_life_goal(self):
        p = self.agent.attributes.personality_vector
        if p["Greed"] > 0.7: self.life_goal = "Wealth"
        elif p["Altruism"] > 0.7: self.life_goal = "Community" # Disabled "Prophet"
        elif p["Curiosity"] > 0.7: self.life_goal = "Sage"
        elif p["Aggression"] > 0.7: self.life_goal = "Warlord"
        else: self.life_goal = "Community"

    def update_karma(self, amount: float):
        self.soul.karma += amount
        
    def review_plan(self, plan: Dict, world) -> Dict:
        """
        The Conscience. Can veto or modify Qalb's plan.
        """
        # Example: If Qalb wants to Steal (not impl yet), Ruh might forbid it based on Karma.
        # Example: If Life Goal is "Sage", bias towards exploration/knowledge.
        
        if self.life_goal == "Sage" and plan['action'] == 'wander':
            # Upgrade wander to 'explore_new_zone'
            return {'action': 'explore', 'desc': "Seeking wisdom in the unknown."}
            
        # Example Implementation of "Fasting" (Spiritual override)
        # If today is a holy day (mock logic), refuse to eat? (Maybe too complex for now)
        
        return plan # Approve by default

# --- MAIN AGENT CLASS ---

class Agent:
    def __init__(self, x: int, y: int, name: str = None, gender: str = None, soul: Soul = None, birth_time: int = 0):
        self.id = str(uuid.uuid4())
        self.x = x
        self.y = y
        self.birth_time = birth_time
        
        # Identity
        if gender is None: 
            # Force 50/50 distribution roughly using random choice
            gender = np.random.choice(['male', 'female'], p=[0.5, 0.5])
        if name is None: name = np.random.choice(NAMES_MALE if gender == 'male' else NAMES_FEMALE)
        
        # Personality
        p_vector = {trait: np.random.random() for trait in PERSONALITY_TRAITS}
        
        self.attributes = AgentAttributes(name=name, gender=gender, personality_vector=p_vector)
        self.state = AgentState()
        
        # Inventory & Knowledge
        # Inventory & Knowledge
        self.inventory: List[Dict] = [] # [{'item': ..., 'count': ...}]
        self.knowledge: List[str] = []
        self.diary: List[str] = []
        self.visible_agents: List[str] = [] # List of names of currently seen agents
        
        # Spatial Memory
        
        # Spatial Memory
        # { 'food': [(x,y), (x,y)], 'water': [], 'agent': [(x,y,id)] }
        self.spatial_memory: Dict[str, List[Tuple[int, int]]] = {
            'food': [],
            'wood': [],
            'stone': [],
            'agent': []
        }
        
        # TRI-PARTITE SYSTEM
        self.nafs = Nafs(self)
        self.qalb = Qalb(self)
        self.ruh = Ruh(self, soul)
        
        # Initialize attributes
        self.attributes.curiosity = p_vector["Curiosity"]
        self.attributes.honesty = p_vector["Altruism"]
        self.attributes.aggression = p_vector["Aggression"]
        
        # Determine Game Strategy
        self.determine_strategy()
        
        # Previous Agent compatibility
        self.needs = self.nafs # Alias for simplicity if needed, but better to use .nafs explicitly
        # But we need to expose needs.hunger etc for serialization 
        
        # Movement Memory
        self.last_x, self.last_y = x, y
        self.plan_queue: List[Dict] = []
        
        # Log birth
        self.log_diary(f"I am born. I am {self.attributes.name}. My spirit goal is {self.ruh.life_goal}.")
        if self.ruh.soul.past_lives > 0:
            self.log_diary(f"I remember... this is life #{self.ruh.soul.past_lives + 1}.")

    # --- CORE LOOP ---

    def act(self, step_count: int, world):
        """
        The Main Execution Cycle.
        """
        # 0. Cooldown Check (Busy)
        if self.state.busy_until > world.time_step:
            return

        self.state.age_steps += 1
        
        # 1. Update Internal Systems
        self.nafs.update(world)
        self.qalb.update(world)
        
        # 1.5 Perception (Vision)
        self.scan_surroundings(world)

        # 2. MULTITASKING KERNEL
        # If socially locked, run the conversation loop IN PARALLEL
        if self.state.social_lock_target and self.state.social_lock_steps > 0:
             # Check distance to target
             target = world.agents.get(self.state.social_lock_target)
             if target and self.distance_to(target) < 4.0:
                 # We can talk while working
                 self.process_social_loop(world)
                 # Do NOT return. Continue to physical action.
             else:
                 # Too far, break loop
                 self.state.social_lock_target = None
                 self.state.social_lock_steps = 0
                 self.log_diary("Social connection lost (distance).")

        # 3. Decision Pipeline
        
        # A. Nafs Override (Survival Instinct)
        action_plan = self.nafs.check_survival_instinct(world)
        
        if action_plan:
             self.log_diary(f"DEBUG: Nafs Override {action_plan['action']}")
        
        # B. Qalb Proposal (Rational/Social Mind)
        if not action_plan:
            action_plan = self.qalb.propose_action(world)
            
            # C. Ruh Review (Spiritual Veto/Modifier)
            action_plan = self.ruh.review_plan(action_plan, world)
            
        # 4. Execution
        self.execute_action(action_plan, world)
        
    def execute_action(self, plan: Dict, world):
        """Dispatches the action."""
        action = plan['action']
        
        if action == 'flee':
            target = plan.get('target')
            if target: self.flee(target, world)
            
        elif action == 'panic_search':
            # Random move
            self.move_random(world)
            # Try gather
            self.gather(world)
            
        elif action == 'wander':
            self.move_random(world)
            self.gather(world) # Opportunistic
            
        elif action == 'find_resource':
            res_type = plan.get('resource')
            # Check Memory
            target = None
            mem_type = 'food' if res_type == 'consumable' else 'wood' # simplified
            
            knowns = self.spatial_memory.get(mem_type, [])
            if knowns:
                # Find nearest known
                # Sort by distance
                knowns.sort(key=lambda p: (p[0]-self.x)**2 + (p[1]-self.y)**2)
                target = knowns[0]
                
                # Go there
                if (target[0]-self.x)**2 + (target[1]-self.y)**2 < 2:
                    self.gather(world)
                    # If empty, remove from memory
                    if target not in world.items_grid:
                        knowns.pop(0)
                        self.move_random(world)
                else:
                    # dx, dy = target[0] - self.x, target[1] - self.y
                    # mx = 1 if dx > 0 else -1 if dx < 0 else 0
                    # my = 1 if dy > 0 else -1 if dy < 0 else 0
                    # world.move_agent(self.id, mx, my)
                    self.navigate_to(target[0], target[1], world)
            else:
                # Explore (Smart Wander)
                self.move_random(world)
                self.gather(world)
            
        elif action == 'sleep':
            # NO SLEEPING. Wasting time.
            # Redistribute energy magically or just ignore
            self.nafs.energy = min(1.0, self.nafs.energy + 0.1) # Fast recharge
            # Do something productive
            self.move_random(world)
            self.gather(world)
            
        elif action == 'continue_social':
             self.process_social_loop(world)
             
        elif action == 'socialize':
            self.qalb_socialize(world)
            
        elif action == 'gather_materials':
             self.move_random(world)
             self.gather(world)
             
        elif action == 'reproduce':
             self.reproduce_in_game(world)
             
        elif action == 'attack':
             target_id = plan.get('target_id')
             target = world.agents.get(target_id)
             if target:
                 self.combat(target, world)
             else:
                 self.log_diary("My enemy has vanished.")
                 
        # --- Low Level Brain Actions ---
        elif action == 'wait':
            pass
        elif action == 'step_x':
            world.move_agent(self.id, plan['val'], 0)
        elif action == 'step_y':
            world.move_agent(self.id, 0, plan['val'])
        elif action == 'interact':
            # Try gather first, then eat
            # This is "smart" interaction context for the brain
            pos = (self.x, self.y)
            if pos in world.items_grid:
                self.gather(world)
            else:
                self.eat_from_inventory()
    
    def die(self, world, cause="unknown"):
        if self.id not in world.agents: return
        self.log_diary(f"Died of {cause}.")
        print(f"Agent {self.attributes.name} died of {cause}.")
        
        # Reincarnation Logic (Evolution)
        # We don't spawn immediately here (handled by world births), but we save the soul?
        # For now, just remove from world.
        del world.agents[self.id]
        
    def scan_surroundings(self, world):
        """
        Probabilistic Infinite Vision.
        Probability of seeing = 1.0 / (1.0 + max(0, dist - 20) * 0.1)
        Near (<=20): 100%
        Far (>20): Decays.
        """
        # We cannot iterate ALL items in world every step for every agent (O(N^2)). 
        # But for limited N (~50 agents, ~100 items?), it is okay.
        # Let's optimize: Only scan if not busy? No, perception is passive.
        # Clear agent memory for fresh scan
        if 'agent' not in self.spatial_memory: self.spatial_memory['agent'] = []
        
        # Cleanup old memories (older than 500 steps)
        self.spatial_memory['agent'] = [m for m in self.spatial_memory['agent'] if world.time_step - m.get('time', 0) < 500]
        
        self.visible_agents = [] # Reset per frame
        
        # 1. Scan Items (Food/Wood/Stone)
        
        # 1. Scan Items (Food/Wood/Stone)
        # Note: In a real large grid, we would use a spatial index (Quadtree). 
        # For 100x100 grid, raw iteration over dictionary keys is fast enough.
        
        for pos, items in world.items_grid.items():
            dist = np.sqrt((self.x - pos[0])**2 + (self.y - pos[1])**2)
            
            # Probabilistic Vision (100% at 20, ~66% at 30)
            prob = 1.0
            if dist > 20: 
                prob = 1.0 / (1.0 + (dist - 20) * 0.05)
            
            if np.random.random() < prob:
                # Seen! Memorize.
                # Simplified: Just store 'food' or type
                item_name = items[0].name.lower()
                category = 'food' if 'consumable' in items[0].tags else 'item'
                if 'wood' in item_name: category = 'wood'
                if 'rock' in item_name or 'stone' in item_name: category = 'stone'
                
                # Add to memory (Set logic)
                if pos not in self.spatial_memory.get(category, []):
                     if category not in self.spatial_memory: self.spatial_memory[category] = []
                     self.spatial_memory[category].append(pos)

        # 2. Scan Agents (Social)
        for other in world.agents.values():
            if other.id == self.id: continue
            dist = self.distance_to(other)
             
            # Probabilistic Vision
            prob = 1.0
            if dist > 20:
                prob = 1.0 / (1.0 + (dist - 20) * 0.05)
            
            if np.random.random() < prob:
                # Add to known agents (We use opinions dict for now, or spatial)
                # Let's add to spatial memory 'agent'
                if 'agent' not in self.spatial_memory: self.spatial_memory['agent'] = []
                # Remove if exist (inefficient but needed to update pos)
                # self.spatial_memory['agent'] = [pos for pos in self.spatial_memory['agent'] if pos[2] != other.id] # Tuple doesn't have ID in spatial def?
                # Definition: self.spatial_memory: Dict[str, List[Tuple[int, int]]]
                # We need ID to track who it is. Update definition or use opinions.
                # Opinions has persistent ID. Use that for identification.
                # Spatial memory is for "Resource Locations".
                # For agents, let's just use a separate list in memory or update opinions 'last_seen'
                # For the 'Proximity Bonus' in propose_action, we need positions.
                # Let's simple append (x,y) to 'agent' list, clear it every step? 
                # Better: In propose_action, use `world.agents` directly if we allow "Sense" there.
                # But we want strict memory.
                # Let's just append to spatial_memory['agent'] tuple (x,y)
                # self.spatial_memory['agent'].append((other.x, other.y))
                
                # STORE MEMORY WITH TIMESTAMPS
                # Check if we already have this agent in memory, update it
                mem_entry = next((m for m in self.spatial_memory['agent'] if m['id'] == other.id), None)
                if mem_entry:
                    mem_entry['pos'] = (other.x, other.y)
                    mem_entry['time'] = world.time_step
                else:
                    self.spatial_memory['agent'].append({'pos': (other.x, other.y), 'id': other.id, 'time': world.time_step})
                
                # DEBUG: Log sighting
                self.log_diary(f"DEBUG: Saw {other.attributes.name} at {dist:.1f}")
                self.visible_agents.append(other.attributes.name)


    def reproduce_in_game(self, world):
        p_id = self.attributes.partner_id
        partner = world.agents.get(p_id)
        if not partner: return
        
        # Check Proximity
        if self.distance_to(partner) < 2:
             if self.attributes.gender == partner.attributes.gender:
                 return # No biological reproduction for same gender (Sim rules)
             
             # Strict Requirement: Must be happy and healthy
             if self.state.health < 0.8 or partner.state.health < 0.8:
                 return

             # Probability Logic:
             # 0.1 chance for Twins (2)
             # 0.5 chance for Single (1)
             # Remaining 0.4 = Failure
             
             rand = np.random.random()
             children_count = 0
             
             if rand < 0.1:
                 children_count = 2
             elif rand < 0.6:
                 children_count = 1
                 
             if children_count > 0:
                 self.log_diary(f"A magical moment with {partner.attributes.name}... We are blessed with {children_count} child(ren)!")
                 partner.log_diary(f"A magical moment with {self.attributes.name}... We are blessed with {children_count} child(ren)!")
                 
                 for _ in range(children_count):
                     if hasattr(world, 'spawn_child'):
                         world.spawn_child(self, partner)
                         
                 # Cooldown only on success? Or attempt?
                 # Let's cooldown on attempt to prevent spamming the milestone if it lingered (though milestone check prevents that)
                 self.state.busy_until = world.time_step + 100 # Long recovery
                 partner.state.busy_until = world.time_step + 100
             else:
                 self.log_diary("We tried for a child, but the spirits were silent.")
        else:
             # Move towards partner
             dx = partner.x - self.x
             dy = partner.y - self.y
             mx = 1 if dx > 0 else -1 if dx < 0 else 0
             my = 1 if dy > 0 else -1 if dy < 0 else 0
             world.move_agent(self.id, mx, my)

    def combat(self, target, world):
        # Move to target
        if self.distance_to(target) > 1.5:
             dx = target.x - self.x
             dy = target.y - self.y
             mx = 1 if dx > 0 else -1 if dx < 0 else 0
             my = 1 if dy > 0 else -1 if dy < 0 else 0
             world.move_agent(self.id, mx, my)
             return

        # Attack
        damage = 0.2 + (self.attributes.aggression * 0.5)
        target.state.health -= damage
        self.log_diary(f"I attacked {target.attributes.name}!")
        target.log_diary(f"I was attacked by {self.attributes.name}!")
        
        # Karma Penalty
        self.ruh.update_karma(-20.0)
        
        if target.state.health <= 0:
            target.die(world, f"killed by {self.attributes.name}")
            self.ruh.update_karma(-100.0) # Murder is heavy
            self.log_diary(f"I killed {target.attributes.name}. May the Void forgive me.")
    
    # --- ACTIONS ---

    def move_random(self, world):
        # 1. Follow Leader (Swarm Bias)
        if self.attributes.leader_id and self.attributes.leader_id != self.id:
            leader = world.agents.get(self.attributes.leader_id)
            if leader:
                # 20% bias to move towards leader
                if np.random.random() < 0.2:
                    dx = leader.x - self.x
                    dy = leader.y - self.y
                    # Normalize
                    mx = 1 if dx > 0 else -1 if dx < 0 else 0
                    my = 1 if dy > 0 else -1 if dy < 0 else 0
                    self.state.momentum_dir = (mx, my)

        # PERCEPTION-AWARE EXPLORATION
        # Instead of blind momentum, look ahead.
        current_dir = self.state.momentum_dir
        
        # 1. Check if current direction is valid (Land)
        is_valid = False
        if current_dir != (0,0):
             nx, ny = self.x + current_dir[0], self.y + current_dir[1]
             if 0 <= nx < world.width and 0 <= ny < world.height:
                 if world.terrain_grid[ny][nx] != 0: # Land
                     is_valid = True
        
        # 2. If valid and lucky, keep going (Momentum)
        if is_valid and np.random.random() < 0.8:
             next_dir = current_dir
        else:
             # 3. Pick a new valid direction
             # Scan all 8 neighbors
             options = []
             for dx in [-1, 0, 1]:
                 for dy in [-1, 0, 1]:
                     if dx == 0 and dy == 0: continue
                     
                     nx, ny = self.x + dx, self.y + dy
                     if 0 <= nx < world.width and 0 <= ny < world.height:
                         tile_type = world.terrain_grid[ny][nx]
                         if tile_type != 0: # It is Land
                             # Weighting?
                             weight = 1.0
                             # Bias forward (soft turn) if we had momentum
                             if current_dir != (0,0):
                                 dot = dx*current_dir[0] + dy*current_dir[1]
                                 if dot > 0: weight += 2.0 # Forward
                                 if dot < 0: weight *= 0.1 # Backward (turn around only if stuck)
                             
                             options.append(((dx, dy), weight))
             
             if options:
                 # Weighted random choice
                 total_w = sum(o[1] for o in options)
                 r = np.random.uniform(0, total_w)
                 upto = 0
                 next_dir = (0, 0)
                 for d, w in options:
                     if upto + w >= r:
                         next_dir = d
                         break
                     upto += w
             else:
                 next_dir = (0, 0) # Trapped?

        self.state.momentum_dir = next_dir
        if next_dir != (0, 0):
            world.move_agent(self.id, next_dir[0], next_dir[1])

    def flee(self, threat, world):
        dx = self.x - threat.x
        dy = self.y - threat.y
        # Normalize
        mx = 1 if dx > 0 else -1 if dx < 0 else 0
        my = 1 if dy > 0 else -1 if dy < 0 else 0
        world.move_agent(self.id, mx, my)

    def navigate_to(self, tx, ty, world):
        """
        Smart navigation using BFS to avoid water/obstacles.
        Refreshes path every step (for simplicity) or uses cached path.
        """
        # 1. Try naive match first (Optimization)
        dx = tx - self.x
        dy = ty - self.y
        mx = 1 if dx > 0 else -1 if dx < 0 else 0
        my = 1 if dy > 0 else -1 if dy < 0 else 0
        
        # Check if direct move is blocked by water
        # Boundary check first
        target_x, target_y = self.x + mx, self.y + my
        if 0 <= target_x < world.width and 0 <= target_y < world.height:
             if world.terrain_grid[target_y][target_x] != 0: # Not Water
                 # Safe to move directly
                 world.move_agent(self.id, mx, my)
                 return
        
        # 2. PATHFINDING (BFS)
        # Find shortest path to (tx, ty)
        queue = [(self.x, self.y, [])]
        visited = set()
        visited.add((self.x, self.y))
        
        # Limit depth to prevent lag
        max_depth = 25
        
        found_path = None
        
        while queue:
            cx, cy, path = queue.pop(0)
            
            if len(path) > max_depth: continue
            
            # Neighbors (Up, Down, Left, Right)
            for nx, ny in [(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)]:
                 if 0 <= nx < world.width and 0 <= ny < world.height:
                     if (nx, ny) not in visited:
                         # Check Walkable
                         if world.terrain_grid[ny][nx] != 0: # Not Water
                             visited.add((nx, ny))
                             new_path = list(path)
                             new_path.append((nx, ny))
                             queue.append((nx, ny, new_path))
                             
                             # Early exit if target found or close enough
                             # Exact match might be hard if blocked, so "close enough" logic?
                             # For now, simplistic: Exact or Adjacent to target
                             dist_sq = (nx - tx)**2 + (ny - ty)**2
                             if dist_sq <= 2: 
                                 found_path = new_path
                                 break
            if found_path: break
            
        if found_path:
            # Take first step
            next_step = found_path[0]
            nx, ny = next_step
            # Calculate delta
            ddx = nx - self.x
            ddy = ny - self.y
            world.move_agent(self.id, ddx, ddy)
        else:
            # Fallback: Random (stuck)
            self.move_random(world)

    def gather(self, world):
        # Opportunistic gather
        items = world.items_grid.get((self.x, self.y))
        if items:
            item = items[0]
            if self.can_pickup(item):
                to_take = items.pop(0)
                if not items: del world.items_grid[(self.x, self.y)]
                self._add_to_inventory(to_take)
                self.log_diary(f"Picked up {to_take.name}.")

    def can_pickup(self, item) -> bool:
        # Simple cap
        count = sum([s['count'] for s in self.inventory if s['item']['name'] == item.name])
        if count >= 10: return False
        return True

    def _add_to_inventory(self, item):
        for slot in self.inventory:
            if slot['item']['name'] == item.name:
                slot['count'] += 1
                return
        self.inventory.append({'item': item.to_dict(), 'count': 1})

    def eat_from_inventory(self) -> bool:
        for i, slot in enumerate(self.inventory):
            if "consumable" in slot['item']['tags']:
                slot['count'] -= 1
                self.nafs.hunger = max(0.0, self.nafs.hunger - 0.5)
                self.log_diary(f"Ate {slot['item']['name']}.")
                if slot['count'] <= 0: self.inventory.pop(i)
                return True
        return False
        
    def qalb_socialize(self, world):
        """
        Complex Social Logic: Hierarchy, Herding, and Chat Loops.
        """
        # 1. Vision Filter (Who can I see?)
        candidates = []
        for other in world.agents.values():
            if other.id == self.id: continue
            dist = self.distance_to(other)
            
            # Probabilistic Vision (100% at 20, ~66% at 30)
            prob = 1.0
            if dist > 20: prob = 1.0 / (1.0 + (dist - 20) * 0.05)
            
            # Family/Friends are always sensed (Psychic Link)
            if other.id == self.attributes.partner_id or other.id in self.attributes.friend_ids:
                prob = 1.0
                
            if np.random.random() < prob:
                candidates.append((dist, other))
        
        cand_count = len(candidates)
        print(f"Agent {self.attributes.name} scanning social... Found {cand_count} candidates.")
        
        candidates.sort(key=lambda x: x[0])
        
        # 2. Decision: Interact or Move?
        if not candidates: 
            # print(f"  Agent {self.attributes.name}: No visible candidates.")
            self.log_diary("DEBUG: Socialize - No visible agents")
            
            # SEEK LAST KNOWN LOCATION (Persistent Memory)
            known_agents = self.spatial_memory.get('agent', [])
            if known_agents:
                # Sort by time (recency)
                known_agents.sort(key=lambda m: m['time'], reverse=True)
                last_seen = known_agents[0]
                tx, ty = last_seen['pos']
                
                dist_to_mem = np.sqrt((self.x - tx)**2 + (self.y - ty)**2)
                
                if dist_to_mem > 2:
                    print(f"  Agent {self.attributes.name}: Seeking memory of agent at {tx},{ty}")
                    # Move towards it
                    dx = tx - self.x
                    dy = ty - self.y
                    mx = 1 if dx > 0 else -1 if dx < 0 else 0
                    my = 1 if dy > 0 else -1 if dy < 0 else 0
                    world.move_agent(self.id, mx, my)
                    return
                else:
                     # We arrived but they are gone. Remove memory.
                     self.spatial_memory['agent'].pop(0)
            
            self.move_random(world)
            return

        nearest_dist, nearest = candidates[0]
        # print(f"  Agent {self.attributes.name}: Nearest {nearest.attributes.name} at {nearest_dist:.1f}")
        
        # Priority: Partner -> Leader -> Friend -> Stranger
        target = nearest
        
        # Override Target: If I have a leader or partner far away, go to them.
        # But for now, stick to nearest visible for interaction.
        
        # A. INTERACTION (Close Range <= 2.0)
        if nearest_dist <= 2.0:
            # Check if target is available
            if target.state.social_lock_target and target.state.social_lock_target != self.id:
                self.log_diary(f"DEBUG: {target.attributes.name} is busy.")
                return

            # Check Cooldown
            if self.qalb.social_cooldowns.get(nearest.id, 0) > world.time_step:
                self.log_diary(f"DEBUG: Resting from social with {nearest.attributes.name}")
                # Maybe move away?
                self.move_random(world)
                return

            # Start MUTUAL Chat Loop
            self.state.social_lock_target = nearest.id
            self.state.social_lock_steps = 5
            
            # Force them to lock onto me (Mutual)
            target.state.social_lock_target = self.id
            target.state.social_lock_steps = 5 
            
            self.log_diary(f"Locked social with {nearest.attributes.name}.")
            self.process_social_loop(world) # Do first step now
            return
        else:
            # Approach Logic
            self.log_diary(f"Approaching {nearest.attributes.name} ({nearest_dist:.1f})")
            # Move towards logic is handled below in 'Herding' but we should ensure we move TO them if we want to socialize
            # Force strict movement to Nearest if intending to socialize
            # dx = nearest.x - self.x
            # dy = nearest.y - self.y
            # mx = 1 if dx > 0 else -1 if dx < 0 else 0
            # my = 1 if dy > 0 else -1 if dy < 0 else 0
            # world.move_agent(self.id, mx, my)
            self.navigate_to(nearest.x, nearest.y, world)
            return

        # B. MOVEMENT (Herding)
        # Calculate attraction/repulsion vector
        vec_x, vec_y = 0.0, 0.0
        
        for dist, other in candidates:
            op = self.qalb.opinions.get(other.id, 0.0)
            
            # FRIENDS (Op > 5) -> Attract
            if op > 5 or other.id == self.attributes.partner_id:
                force = 10.0 / (dist + 0.1)
                vec_x += (other.x - self.x) * force
                vec_y += (other.y - self.y) * force
                
            # ENEMIES (Op < -5) -> Repel
            elif op < -5:
                force = 10.0 / (dist + 0.1)
                vec_x -= (other.x - self.x) * force
                vec_y -= (other.y - self.y) * force
        
        # If no strong opinions, just go to nearest (Desire to socialize)
        if vec_x == 0 and vec_y == 0:
            vec_x = nearest.x - self.x
            vec_y = nearest.y - self.y
            
        # Normalize and Move
        mag = np.sqrt(vec_x**2 + vec_y**2)
        if mag > 0:
            mx = 1 if vec_x > 0 else -1 if vec_x < 0 else 0
            my = 1 if vec_y > 0 else -1 if vec_y < 0 else 0
            world.move_agent(self.id, mx, my)
        else:
             self.move_random(world)

    def process_social_loop(self, world):
        target_id = self.state.social_lock_target
        target = world.agents.get(target_id)
        
        if not target or self.distance_to(target) > 3.0:
            # Break Loop (Target lost/left)
            self.state.social_lock_target = None
            self.state.social_lock_steps = 0
            # Set Cooldown
            self.qalb.social_cooldowns[target_id] = world.time_step + 40 # 40 steps timeout
            return
            
        self.log_diary(f"DEBUG: Processing Social Loop with {target.attributes.name}")
            
        # GAME THEORY ROUND (Once per step per pair? No, that's too fast. Once per interaction start?)
        # Let's do it every step but with small impact, or only on first step?
        # User wants "socialize using game theory". 
        # Let's say every step of the lock is a "Round" of the game.
        
        # 1. Decide My Move
        my_move = self.make_game_decision(target_id)
        
        # 2. Decide Their Move (Simulated for equality, or read their state?)
        their_move = target.make_game_decision(self.id)
        
        self.log_diary(f"DEBUG: Moves - Me: {my_move}, Them: {their_move}")
        
        # 3. Payoff Matrix (Standard PD)
        # T > R > P > S
        # Defect/Coop (T) > Coop/Coop (R) > Defect/Defect (P) > Coop/Defect (S)
        # Rewards: Happiness and Social Need
        
        my_payoff = 0.0
        their_payoff = 0.0
        
        score_impact = 0.0 # Opinion change
        
        if my_move == 'cooperate' and their_move == 'cooperate':
            # Reward
            my_payoff = 0.1
            their_payoff = 0.1
            score_impact = 0.5 # We like each other
            self.log_diary(f"Cooperated with {target.attributes.name}. Harmony.")
            
        elif my_move == 'defect' and their_move == 'defect':
            # Punishment
            my_payoff = -0.05
            their_payoff = -0.05
            score_impact = -0.2 # Distrust
            self.log_diary(f"Clashed with {target.attributes.name}. Both defected.")
            
        elif my_move == 'defect' and their_move == 'cooperate':
            # Temptation (I win, they lose)
            my_payoff = 0.2
            their_payoff = -0.2
            score_impact = -0.5 # They hate me now (handled in their update potentially?)
            # But here I am thinking... if I defected and they coop, do I like them?
            # Maybe I think they are a sucker (Dominance).
            self.qalb.opinions[target_id] = self.qalb.opinions.get(target_id, 0) + 0.1 # I exploited them
            
        elif my_move == 'cooperate' and their_move == 'defect':
            # Sucker
            my_payoff = -0.2
            their_payoff = 0.2
            score_impact = -1.0 # Betrayal!
            self.log_diary(f"Betrayed by {target.attributes.name}!")
            
        # Apply Payoffs
        self.state.happiness = min(1.0, max(0.0, self.state.happiness + my_payoff))
        self.qalb.social = min(1.0, self.qalb.social + 0.1) # Interaction always fills social a bit
        
        # Update Memories
        self.qalb.social_memory[target_id] = their_move
        if target_id not in self.qalb.history: self.qalb.history[target_id] = []
        self.qalb.history[target_id].append(their_move)
        
        # We need to update THEIR memory of ME too so next turn is fair?
        # Or let them handle it on their turn? 
        # PROBLEM: If we update them, and they act later in the loop, they might double count?
        # Sync issue. 
        # Simplification: Only update MY state. When THEY act, they will check me.
        # But wait, 'their_move' was hypothetical? No, we called the function.
        # We should probably NOT change their state here, only mine.
        # BUT: For consistent Game Theory, we need simultaneous moves.
        # Let's assume on their turn, they will do the same against me.
        # So I only process MY rewards and MY memory of THEM.
        
        # Update Opinion
        curr_op = self.qalb.opinions.get(target_id, 0.0)
        new_op = curr_op + score_impact
        self.qalb.opinions[target_id] = new_op
        
        # RELATIONSHIP THRESHOLDS
        # Rivals
        if new_op <= -30 and curr_op > -30:
             self.log_diary(f"{target.attributes.name} is now my RIVAL!")
        # Friends
        if new_op >= 10 and curr_op < 10:
             self.log_diary(f"{target.attributes.name} is now my Friend.")
             self.attributes.friend_ids.append(target_id)
        # Best Friends
        if new_op >= 20 and curr_op < 20:
             self.log_diary(f"{target.attributes.name} is my Best Friend!")
        # Lovers
        if new_op >= 30 and curr_op < 30:
             if self.attributes.gender != target.attributes.gender:
                 self.log_diary(f"I am in love with {target.attributes.name}!")
                 self.attributes.partner_id = target_id
             else:
                 self.log_diary(f"{target.attributes.name} is my Brother/Sister in arms!")

        # REPRODUCTION (Every 60 points)
        # Check if we crossed a multiple of 60 boundary
        # e.g., 59 -> 60, 119 -> 120
        if self.attributes.partner_id == target_id:
             # REPRODUCTION THRESHOLD: Check multiples of 60 explicitly
             # We want to trigger ONLY if we just crossed the specific boundary
             op_threshold = 60.0
             if int(new_op / op_threshold) > int(curr_op / op_threshold):
                  if self.attributes.gender != target.attributes.gender: # Double check
                      # Check Population Cap (Soft cap at 100)
                      if len(world.agents) < 100:
                          self.log_diary(f"A magical moment with {target.attributes.name}...")
                          self.reproduce_in_game(world)
                      else:
                          self.log_diary("We want a child, but the world is too crowded.")

        # POLITICS & LEADERSHIP
        # 1. Assert Leadership (Alpha)
        my_leadership_score = self.attributes.aggression + self.attributes.personality_vector["Social"]
        their_leadership_score = target.attributes.aggression + target.attributes.personality_vector["Social"]
        
        # If I am charismatic and dominant, and they are weaker
        if my_leadership_score > 1.4 and my_leadership_score > their_leadership_score + 0.3:
            # "Kneel before Zod"
            if not self.attributes.leader_id:
                self.attributes.leader_id = self.id # I am my own leader
                self.log_diary("I am the Alpha.")
                
                # FOUND TRIBE if not exists
                if not self.attributes.tribe_id:
                     tribe = world.create_tribe(f"{self.attributes.name}'s Tribe", self.id)
                     self.attributes.tribe_id = tribe.id
            
            if target.attributes.leader_id != self.id:
                 # Attempt Convert
                 if np.random.random() < 0.3: # 30% chance they concede
                     # Join my Tribe
                     if self.attributes.tribe_id:
                         world.join_tribe(target.id, self.attributes.tribe_id)
                         target.attributes.leader_id = self.id
                         self.log_diary(f"Recruited {target.attributes.name} to {world.tribes[self.attributes.tribe_id].name}.")
                         target.log_diary(f"I pledge allegiance to {self.attributes.name}.")
                     
        # 2. Recruit for my Leader (Beta)
        elif self.attributes.leader_id and self.attributes.leader_id != self.id:
             # "Have you heard of our lord?"
             if target.attributes.leader_id != self.attributes.leader_id:
                 leader_tribe_id = self.attributes.tribe_id
                 if leader_tribe_id:
                     if np.random.random() < 0.1:
                         world.join_tribe(target.id, leader_tribe_id)
                         target.attributes.leader_id = self.attributes.leader_id
                         self.log_diary(f"Convinced {target.attributes.name} to join our tribe.")

        # SET GOALS (As Leader)
        if self.attributes.leader_id == self.id and self.attributes.tribe_id:
            # Update Tribe Goal
            tribe = world.tribes.get(self.attributes.tribe_id)
            if tribe:
                if self.nafs.hunger > 0.6: tribe.set_goal("gather_food")
                else: tribe.set_goal("gather_wood")
            
        # FOLLOW ORDERS (As Follower) is handled in execute command or passive goal sync
            
        # Decrement timer
        self.state.social_lock_steps -= 1
        if self.state.social_lock_steps <= 0:
             self.state.social_lock_target = None
             # Set Cooldown
             self.qalb.social_cooldowns[target_id] = world.time_step + 60

    def determine_strategy(self):
        p = self.attributes.personality_vector
        aggr = p.get("Aggression", 0.5)
        altr = p.get("Altruism", 0.5)
        forg = p.get("Forgiveness", 0.5)
        
        if p["Aggression"] > 0.7:
             self.attributes.strategy = GameStrategy.GRIM_TRIGGER.value # Or Bully
        elif p["Altruism"] > 0.7:
             self.attributes.strategy = GameStrategy.TIT_FOR_TAT.value
        elif p["Impulsivity"] > 0.8:
             self.attributes.strategy = GameStrategy.RANDOM.value
             
        # PROPHET LOGIC
        # PROPHET LOGIC - DISABLED
        # if p.get("Spirituality", 0) > 0.85 and p["Social"] > 0.8:
        #      self.attributes.is_prophet = True
        #      self.attributes.strategy = GameStrategy.ALWAYS_COOPERATE.value
        #      self.attributes.ranking = 1.0 # Max influence
        #      self.log_diary("I have seen the Truth. I am a Prophet.")
        # else: 
        self.attributes.strategy = GameStrategy.TIT_FOR_TAT.value # Default
        
    def make_game_decision(self, opponent_id: str) -> str:
        strat = self.attributes.strategy
        history = self.qalb.history.get(opponent_id, [])
        last_move_them = self.qalb.social_memory.get(opponent_id, None)
        
        # 1. Defaults
        if not history:
            # First move: Cooperate usually, unless aggressive
            if strat in [GameStrategy.ALWAYS_DEFECT.value, GameStrategy.BULLY.value]: return 'defect'
            if strat == GameStrategy.RANDOM.value: return np.random.choice(['cooperate', 'defect'])
            return 'cooperate' # TFT, Pavlov, etc start nice
            
        # 2. Strategies
        if strat == GameStrategy.ALWAYS_COOPERATE.value: return 'cooperate'
        if strat == GameStrategy.ALWAYS_DEFECT.value: return 'defect'
        
        if strat == GameStrategy.RANDOM.value: 
            return np.random.choice(['cooperate', 'defect'])
            
        if strat == GameStrategy.TIT_FOR_TAT.value:
            return last_move_them if last_move_them else 'cooperate'
            
        if strat == GameStrategy.TIT_FOR_TWO_TATS.value:
            # Defect only if last 2 were defects
            if len(history) >= 2 and history[-1] == 'defect' and history[-2] == 'defect':
                return 'defect'
            return 'cooperate'
            
        if strat == GameStrategy.GRIM_TRIGGER.value or strat == GameStrategy.UNFORGIVING.value:
            if 'defect' in history: return 'defect'
            return 'cooperate'
            
        if strat == GameStrategy.PAVLOV.value:
            # Win-Stay, Lose-Switch
            # If I played X and got Reward (They coop), Stay X.
            # If I played X and got Sucker/Punish (They defect), Switch.
            # We need to know MY last move.
            # This requires storing my history too? 
            # Approximate: Pavlov coops if we agreed (CC or DD), defects if we disagreed (CD or DC).
            # Wait, standard Pavlov: 
            # If opponent cooperated -> Play what I played last time.
            # If opponent defected -> Switch what I played last time.
            # Lets treat it simplified: Coop if we acted same last round?
            return last_move_them # Placeholder, actually Pavlov is complex without my history.
            # Let's fallback to TFT to avoid crash or strict logic
            return last_move_them             

        if strat == GameStrategy.BULLY.value:
             # Defect first. If they defect back, maybe coop to appease?
             # Simple Bully: Always defect unless punished?
             # Let's say: Defect. But if they defected last time, Cooperate (Chicken out).
             if last_move_them == 'defect': return 'cooperate'
             return 'defect'
             
        if strat == GameStrategy.PEACEMAKER.value:
            # TFT but 10% chance to forgive defect
            if last_move_them == 'defect':
                if np.random.random() < 0.2: return 'cooperate'
                return 'defect'
            return 'cooperate'
            
        return 'cooperate'

    # --- HELPERS ---

    def distance_to(self, entity) -> float:
        return np.sqrt((self.x - entity.x)**2 + (self.y - entity.y)**2)

    def log_diary(self, entry: str):
        self.diary.append(f"[Life {self.ruh.soul.past_lives}] {entry}")
        if len(self.diary) > 50: self.diary.pop(0)

    def add_memory(self, desc: str, type="event", impact=0.0):
        self.ruh.soul.memories.append(Memory(type=type, description=desc, location=(self.x, self.y), time=self.state.age_steps, emotional_impact=impact))

    def to_dict(self, world=None):
        """
        Serializer for Frontend/API.
        Adapts the new structure to a flat JSON compatible with existing props where possible,
        but exposes the new structure too.
        """
        return {
            "id": self.id,
            "x": int(self.x),
            "y": int(self.y),
            "attributes": self.attributes.__dict__,
            "state": self.state.__dict__,
            "needs": { # Flattened view for frontend compatibility
                "hunger": self.nafs.hunger,
                "energy": self.nafs.energy,
                "social": self.qalb.social,
                "fun": self.qalb.fun
            },
            "nafs": {k:v for k,v in self.nafs.__dict__.items() if k != 'agent'},
            "qalb": {k:v for k,v in self.qalb.__dict__.items() if k != 'agent' and k != 'brain'}, # Exclude brain object too (PPO model not serializable)
            "ruh": {
                "life_goal": self.ruh.life_goal,
                "wisdom": self.ruh.wisdom,
                "karma": self.ruh.soul.karma,
                "past_lives": self.ruh.soul.past_lives
            },
            "strategy": self.attributes.strategy,
            "social_memory": self.qalb.social_memory,
            "inventory": self.inventory,
            "diary": self.diary,
            "visible_agents": self.visible_agents,
            # Tribe Info
            "tribe_id": self.attributes.tribe_id,
            "tribe_name": world.tribes[self.attributes.tribe_id].name if world and self.attributes.tribe_id and self.attributes.tribe_id in world.tribes else "Nomad",
            "tribe_goal": world.tribes[self.attributes.tribe_id].goal if world and self.attributes.tribe_id and self.attributes.tribe_id in world.tribes else "wander",
            "generation": self.attributes.generation
        }
    
    def get_observation(self, world):
        """
        Constructs the observation vector for the RL brain.
        Matches AdamBaseEnv space (77 floats).
        """
        # 5x5 Grid around agent
        obs = np.zeros(77, dtype=np.float32)
        
        # Fill grid
        # Channels: 0: EntityType (1=Agent, 0.5=Animal), 1: ID (Hash?), 2: Property (Hunger/Health?)
        # Simplified: Channel 0: Obstacle/Terrain, 1: Food/Item, 2: Agent/Animal
        
        idx = 0
        grid_radius = 2 # 5x5
        
        for dy in range(-grid_radius, grid_radius + 1):
            for dx in range(-grid_radius, grid_radius + 1):
                tx = self.x + dx
                ty = self.y + dy
                
                # Bounds check
                if 0 <= tx < world.width and 0 <= ty < world.height:
                    # Ch 0: Terrain
                    t_type = world.terrain_grid[ty][tx]
                    if t_type == 0: obs[idx] = 1.0 # Water (Blocked)
                    else: obs[idx] = 0.0
                    
                    # Ch 1: Food
                    # Check items
                    if (tx, ty) in world.items_grid:
                        # Assuming any item is 'food' for basic brain
                        obs[idx+1] = 1.0 
                    
                    # Ch 2: Agent
                    if world._get_agent_at(tx, ty):
                        obs[idx+2] = 1.0
                else:
                    # Out of bounds is wall
                    obs[idx] = 1.0
                
                idx += 3
        
        # Internal State (Last 2)
        obs[75] = self.nafs.hunger
        obs[76] = self.state.health
        
        return obs

    # --- COMPATIBILITY SHIMS ---
    
    def load_brain(self, path):
        self.qalb.load_brain(path)
        
    def act_smart(self, world):
        pass


