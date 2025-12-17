from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import uuid
import numpy as np
from enum import Enum
from .brain import AgentBrain

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
    "Seriousness", "Forgiveness", "Vengefulness", "Spirituality", "Skepticism",
    "Conscientiousness"
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
    parents: List[str] = field(default_factory=list) # [parent1_id, parent2_id]
    children: List[str] = field(default_factory=list) # [child1_id, ...]
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
        self.hunger = min(1.0, self.hunger)
        self.energy -= 0.0002
        if self.agent.state.health > 0.8:
            self.lust += 0.005 # Grows faster than hunger if healthy
        
        # --- HEALTH MECHANICS ---
        
        # 1. Starvation Damage
        if self.hunger >= 1.0:
            self.agent.state.health -= 0.02 # Fast death
            if np.random.random() < 0.1: self.agent.log_diary("I am starving to death...")
            
        # 2. Regeneration (Well-fed & Rested)
        if self.hunger < 0.3 and self.energy > 0.5:
             self.agent.state.health += 0.005
             self.agent.state.health = min(1.0, self.agent.state.health)
             
        # 3. Psychosomatic Effects
        happiness = self.agent.state.happiness
        if happiness < 0.2: # Depression
             self.agent.state.health -= 0.001
        elif happiness > 0.8: # Joy
             self.agent.state.health += 0.002
             self.agent.state.health = min(1.0, self.agent.state.health)

    def check_survival_eating(self) -> bool:
        """
        Auto-Eat logic for multitasking.
        If starving (>0.8) and has food, eat immediately as a free action.
        """
        if self.hunger > 0.8:
            if self.agent.eat_from_inventory():
                # self.agent.log_diary("Ate ration on the run.") # Too spammy?
                return True
        return False

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
        elif self.social < 0.2: self.emotional_state = "Lonely"
        else: self.emotional_state = "Neutral"

    def check_passive_social(self, world):
        """
        Multitasking Logic (Philosophy Ch 21).
        Allows socializing while performing other actions (Walking/Gathering).
        """
        # Quick proximity check
        for other_id, state in self.agent.visible_agents_state.items():
            other = world.agents.get(other_id)
            if not other: continue
            
            dist = self.agent.distance_to(other)
            if dist < 3.0:
                # Passive Interaction
                # 1. Update Social Battery
                self.social = min(1.0, self.social + 0.005)
                # self.agent.state.happiness is not directly accessible if self.agent.state is a dataclass?
                # Yes it is: self.agent.state.happiness
                self.agent.state.happiness = min(1.0, self.agent.state.happiness + 0.002)
                
                # 2. Update Opinion (Exposure Effect)
                # Helper update_opinion might be in Qalb? 
                # Let's check Qalb methods. It used to be in Agent.
                # If Qalb has opinions dict, it should manage it.
                # Lines 203: self.opinions = {}
                # I need to ensure update_opinion exists in Qalb or implement it here.
                current_op = self.opinions.get(other_id, 0)
                self.opinions[other_id] = min(100, current_op + 0.1)
                
                # 3. Log occasionally
                if np.random.random() < 0.05:
                    self.agent.log_diary(f"Chatting with {other.attributes.name} while working.")

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
        
        # 6. Discrete Productivity Desires (Wood, Stone, Craft)
        
        # A. Base Industriousness (Personality)
        base_labor = p.get("Conscientiousness", 0.5) * 0.5
        
        # B. Tribe Influence
        tribe_goal = None
        if self.agent.attributes.tribe_id:
             tribe = world.tribes.get(self.agent.attributes.tribe_id)
             if tribe: tribe_goal = tribe.goal

        # C. Calculate Specific Desires
        
        # Find Food (Gathering)
        # Driven by Hunger (Forward planning) + Tribe Goal
        # If hungry, "Eat" is high, but "Find Food" is the means.
        # Let's keep "Eat" as "I need to consume". Action maps to find_food if no food.
        # But here we want explicit "Gathering" desire even if not starving (Hoarding).
        desires["Find Food"] = base_labor * 0.5
        if tribe_goal == "gather_food": desires["Find Food"] += 0.5
        if self.agent.nafs.hunger > 0.4: desires["Find Food"] += 0.3
        
        # Find Wood
        desires["Find Wood"] = base_labor
        if tribe_goal == "gather_wood": desires["Find Wood"] += 0.6
        
        # Find Stone
        desires["Find Stone"] = base_labor
        if tribe_goal == "gather_stone": desires["Find Stone"] += 0.6
        
        # Crafting
        desires["Craft"] = 0.0
        # Check if we have Stone (to make Block) or Stone Block (to make Wall)
        has_stone = any(s['item']['name'] == 'Stone' for s in self.agent.inventory)
        has_block = any(s['item']['name'] == 'Stone Block' for s in self.agent.inventory)
        
        if has_stone: desires["Craft"] += 0.3
        if has_stone and tribe_goal == "build_home": desires["Craft"] += 0.4
        
        desires["Build"] = 0.0
        if has_block: desires["Build"] += 0.4
        if has_block and tribe_goal == "build_home": desires["Build"] += 0.6
        
        # 7. Social Economy (Trade / Gift)
        desires["Trade"] = 0.0
        desires["Gift"] = 0.0
        
        inventory_count = sum([s['count'] for s in self.agent.inventory])
        
        
        # Look at visible neighbors
        for agent_id, state in self.agent.visible_agents_state.items():
             # Distance check (must be close to trade)
             # We need real object to check dist, or just use memory pos. 
             # Simplify: If in visible_agents_state, we assume we can interact if we walk to them?
             # Or we only trade if neighbor is VERY close (< 2).
             # Let's assume we need to approach them.
             
             # GIFTING (Altruism): Friend is needy
             op = self.opinions.get(agent_id, 0) # Raw opinion
             is_friend = op > 20
             is_needy = state['hunger'] > 0.7 or state['health'] < 0.5
             if is_friend and is_needy:
                 if p["Altruism"] > 0.6 and inventory_count > 5:
                     desires["Gift"] = max(desires["Gift"], 0.8)
                     
             # TRADING (Self-Interest): I am needy, they have surplus
             am_needy = self.agent.nafs.hunger > 0.6
             if am_needy and "Food" in str(state['inventory']): # Loose check for food items
                  desires["Trade"] = max(desires["Trade"], 0.7)
                  
             # General Trading (Crafting needs)
             if desires["Find Wood"] > 0.5 and "Wood" in str(state['inventory']):
                  desires["Trade"] = max(desires["Trade"], 0.6)
        
        # DAMPENER: Full Inventory
        inventory_count = sum([s['count'] for s in self.agent.inventory])
        if inventory_count >= 20:
            desires["Find Wood"] *= 0.1
            desires["Find Stone"] *= 0.1
            desires["Find Food"] *= 0.1

        # 8. Violence (Aggression + Rivalry)
        desires["Violence"] = 0.0
        
        # Base Aggression
        if p["Aggression"] > 0.8: desires["Violence"] += 0.2
        
        # Check Neighbors for Rivals
        nearest_rival = None
        min_dist = 999
        
        for agent_id, state in self.agent.visible_agents_state.items():
             op = self.opinions.get(agent_id, 0)
             # Personal Rivalry
             if op < -50:
                 desires["Violence"] = max(desires["Violence"], 0.8)
                 # Find object
                 # (Limit: We only have IDs in visible_agents_state, need object for action target?)
                 # Access world for object (Cheat/Efficiency)
                 rival = world.agents.get(agent_id)
                 if rival:
                     d = self.agent.distance_to(rival)
                     if d < min_dist:
                         min_dist = d
                         nearest_rival = rival
                         
        # Tribe War Check (To be implemented with Tribe updates)
        if self.agent.attributes.tribe_id:
            my_tribe = world.tribes.get(self.agent.attributes.tribe_id)
            if my_tribe and hasattr(my_tribe, 'enemies'): # defensive check
                 for enemies_tribe_id in my_tribe.enemies:
                     # Check if any visible agent is in enemy tribe
                     for agent_id, state in self.agent.visible_agents_state.items():
                         if state.get('tribe_id') == enemies_tribe_id:
                             desires["Violence"] = 1.0 # WAR!
                             rival = world.agents.get(agent_id)
                             if rival: nearest_rival = rival

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
                
        elif dominant_desire == "Find Food":
             return {'action': 'find_resource', 'resource': 'food', 'desc': "Gathering food."}
             
        elif dominant_desire == "Find Wood":
             return {'action': 'find_resource', 'resource': 'wood', 'desc': "Gathering wood."}
             
        elif dominant_desire == "Find Stone":
             return {'action': 'find_resource', 'resource': 'stone', 'desc': "Mining stone."}
             
        elif dominant_desire == "Craft":
             return {'action': 'craft_item', 'target': 'Stone Block', 'desc': "Crafting blocks."}
             
        elif dominant_desire == "Build":
             return {'action': 'build_structure', 'structure': 'Wall', 'desc': "Building boundaries."}
             
        elif dominant_desire == "Gift":
             return {'action': 'social_trade', 'mode': 'gift', 'desc': "Bearing gifts."}
             
        elif dominant_desire == "Trade":
             return {'action': 'social_trade', 'mode': 'barter', 'desc': "Looking to trade."}
             
        elif dominant_desire == "Violence":
             if nearest_rival:
                 return {'action': 'attack_agent', 'target': nearest_rival, 'desc': "Attacking rival!"}
             else:
                 return {'action': 'wander', 'desc': "Hunting for enemies."}
        
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
        self.visible_agents_state: Dict[str, Dict] = {} # ID -> Public State
        
        # Spatial Memory
        
        # Spatial Memory
        # { 'food': [(x,y), (x,y)], 'water': [], 'agent': [(x,y,id)] }
        self.spatial_memory: Dict[str, List[Tuple[int, int]]] = {
            'food': [],
            'wood': [],
            'stone': [],
            'agent': []
        }
        
        # Internal Systems
        self.nafs = Nafs(self)
        self.qalb = Qalb(self)
        self.ruh = Ruh(self, soul)
        self.brain = AgentBrain(self)
        
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

        # 0. Death Check
        if self.state.health <= 0:
            self.die(world)
            return

        self.state.age_steps += 1
        
        # 1. Update Internal Systems
        self.nafs.update(world)
        self.qalb.update(world)
        
        # Tribe Leader Duty
        if self.attributes.tribe_id and self.attributes.leader_id == self.id:
            tribe = world.tribes.get(self.attributes.tribe_id)
            if tribe and (step_count % 100 == 0): # Periodic check
                tribe.assess_needs()
                self.log_diary(f"Tribe Goal Updated: {tribe.goal}")
        
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

        # 2. Decision Making (TRI-PARTITE SYSTEM)
        action_plan = None
        
        # --- OPPORTUNISTIC INTELLIGENCE ---
        # Free Actions that run parallel to main plan
        self.check_opportunistic_gathering(world)
        self.nafs.check_survival_eating()

        # A. Nafs Override (Survival Instinct)
        action_plan = self.nafs.check_survival_instinct(world)
        
        if action_plan:
             self.log_diary(f"DEBUG: Nafs Override {action_plan['action']}")
    
        # B. Brain Planning (Long-term)
        if not action_plan:
            action_plan = self.brain.get_next_action(world)
            if action_plan:
                 self.log_diary(f"BRAIN: Executing plan {action_plan['action']}")

        # C. Qalb Proposal (Rational/Social Mind)
        if not action_plan:
            action_plan = self.qalb.propose_action(world)
            
            # D. Ruh Review (Spiritual Veto/Modifier)
            action_plan = self.ruh.review_plan(action_plan, world)
            
        # 4. Multitasking (Philosophy Ch 21)
        # Always run social checks passively if not sleeping/dead
        if action_plan and action_plan['action'] != 'sleep':
            self.qalb.check_passive_social(world)

        # 5. Execution
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
            
        # --- NEW ACTIONS ---
        elif action == 'join_tribe':
            target_tribe_id = plan.get('tribe_id')
            self.join_tribe(target_tribe_id, world)
            self.gather(world) # Opportunistic
            
        elif action == 'find_resource':
            res_type = plan.get('resource')
            # Check Memory
            target = None
            
            # Map Brain Types to Memory Types
            mem_type = res_type.lower()
            if mem_type in ['consumable', 'fruit', 'berry', 'food']:
                mem_type = 'food'
            elif mem_type in ['rock', 'stone']:
                mem_type = 'stone'
            elif mem_type in ['tree', 'wood']:
                mem_type = 'wood'
            
            knowns = self.spatial_memory.get(mem_type, [])
            if knowns:
                # Find nearest known
                # Sort by distance
                knowns.sort(key=lambda p: (p[0]-self.x)**2 + (p[1]-self.y)**2)
                target = knowns[0]
                
                # Go there
                # Go there
                dist_sq = (target[0]-self.x)**2 + (target[1]-self.y)**2
                
                if dist_sq == 0:
                    # On top: Gather!
                    self.gather(world)
                    # If empty, remove from memory
                    if target not in world.items_grid:
                        knowns.pop(0) # Remove from memory
                        # We are done with this step, wait for next decision
                else:
                    # Move towards
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
             
        elif action == 'social_trade':
         # Find target (nearest visible agent or specific target from plan?)
         # For simplicity, pick nearest visible agent.
         # Ideally plan should have target_id.
         # But propose_action didn't select specific id, just 'anyone'.
         # Let's find best candidate again.
         best_candidate = None
         min_dist = 999
         for other_id, state in self.visible_agents_state.items():
             other = world.agents.get(other_id)
             if not other: continue
             d = self.distance_to(other)
             if d < min_dist:
                 min_dist = d
                 best_candidate = other
         
         if best_candidate:
             if min_dist < 2.0:
                 mode = plan.get('mode', 'barter')
                 self.initiate_trade(best_candidate, mode, world)
             else:
                 # Move towards them
                 self.navigate_to(best_candidate.x, best_candidate.y, world)
         else:
             self.log_diary("Nobody to trade with.")
        elif action == 'socialize':
            self.qalb_socialize(world)
            
        elif action == 'attack_agent':
             target = plan.get('target')
             if target:
                 dist = self.distance_to(target)
                 if dist < 2.0:
                     self.combat_logic(target, world)
                 else:
                     self.navigate_to(target.x, target.y, world)
        
        elif action == 'craft_item':
             # Simplified Crafting: Turn Stone -> Stone Block
             # Logic: Remove 1 Stone, Add 1 Stone Block
             # Check inventory
             stones = [s for s in self.inventory if s['item']['name'] == 'Stone']
             if stones:
                 # Remove 1 stone
                 stones[0]['count'] -= 1
                 if stones[0]['count'] <= 0:
                     self.inventory.remove(stones[0])
                     
                 # Add Stone Block (Magic creation for now, ignoring Item class instantiation detail)
                 # We need to create specific Item object
                 from ..env.item import Item
                 import uuid
                 block = Item(id=f"sb_{uuid.uuid4()}", name="Stone Block", weight=5.0, hardness=0.8, durability=1.0, tags=["material", "building"])
                 self._add_to_inventory(block)
                 self.log_diary("Crafted a Stone Block.")
             else:
                 self.log_diary("Failed to craft: No Stone.")
                 
        elif action == 'eat_from_inventory':
             # Try to eat
             if not self.eat_from_inventory():
                 self.log_diary("Plan Failed: No Food.")
                 # Clear Brain Plan if failed?
                 self.brain.action_queue = []
                 self.brain.current_goal = "Plan Failed"

        elif action == 'build_structure':
             # Place Wall
             items = [s for s in self.inventory if s['item']['name'] == 'Stone Block']
             if items:
                 # Consume Block
                 items[0]['count'] -= 1
                 if items[0]['count'] <= 0: self.inventory.remove(items[0])
                 
                 # Place Wall Item
                 from ..env.item import Item
                 import uuid
                 wall = Item(id=f"wall_{uuid.uuid4()}", name="Wall", weight=100.0, hardness=1.0, durability=10.0, tags=["building", "heavy"])
                 
                 # Placement Logic: Near Tribe Center or Self
                 # For now, place right here. 
                 world._add_item(self.x, self.y, wall)
                 self.log_diary("Built a Wall section.")
             else:
                 self.log_diary("Cannot build: No Blocks.")
            
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
                
                # PUBLIC STATE OBSERVATION
                self.visible_agents_state[other.id] = other.get_public_state()
                
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
                # COHESION BIAS: 30% chance to correct course towards swarm center
                dist = self.distance_to(leader)
                if dist > 3.0: # Too far, catch up
                     if np.random.random() < 0.3:
                        dx = leader.x - self.x
                        dy = leader.y - self.y
                        # Normalize
                        mx = 1 if dx > 0 else -1 if dx < 0 else 0
                        my = 1 if dy > 0 else -1 if dy < 0 else 0
                        self.state.momentum_dir = (mx, my)

        # Apply Momentum (Drift)
        if np.random.random() < 0.6:
             mx, my = self.state.momentum_dir
             if mx != 0 or my != 0:
                 world.move_agent(self.id, mx, my)
                 return
                 
        # Explicit Random
        mx = np.random.randint(-1, 2)
        my = np.random.randint(-1, 2)
        # Update momentum
        self.state.momentum_dir = (mx, my)
        world.move_agent(self.id, mx, my)

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
        """
        Gather resources with Tool Multiplier and Depletion.
        """
        items = world.items_grid.get((self.x, self.y))
        if items:
            to_take = items[0] # Don't pop yet
            
            # 1. Tool Logic
            multiplier = 1
            tool_tags = []
            
            # Check Inventory for best tool
            for slot in self.inventory:
                tags = slot['item'].get('tags', [])
                if "tool" in tags:
                     # Check compatibility
                     if to_take.name == "Wood" and "cutting" in tags: 
                         multiplier = 2
                     if to_take.name == "Stone" and "mining" in tags:
                         multiplier = 2
            
            # 2. Add to Inventory
            if self.can_pickup(to_take):
                 # Take the item
                 items.pop(0)
                 if not items: del world.items_grid[(self.x, self.y)]
                 
                 # Add base item
                 self._add_to_inventory(to_take)
                 
                 # Bonus Yield (Magic clone)
                 if multiplier > 1:
                     count = multiplier - 1
                     for _ in range(count):
                         self._add_to_inventory(to_take) # Adds by name stacking
                         
                 self.log_diary(f"Gathered {to_take.name} (x{multiplier}).")
                 
                 # 3. Terrain Degradation (Resource Depletion)
                 # If we took Wood from Forest, it becomes Grass
                 if to_take.name == "Wood":
                     current_terrain = world.terrain_grid[self.y][self.x]
                     if current_terrain == 3: # Forest
                         world.terrain_grid[self.y][self.x] = 2 # Grass
                         
                 # If we took Stone from Mountain, well, mountains are big. 
                 # But maybe if it was a surface rock, it's gone.
                 # Let's say if we mine Stone, there's a small chance to degrade mountain? 
                 # Or just remove the item is enough for now as per user request (stones disappear).
                 # The item removal is handled by items.pop(0).
                 pass
            else:
                 self.log_diary(f"Inventory full. Cannot gather {to_take.name}.")

    def can_pickup(self, item) -> bool:
        # Simple cap
        count = sum([s['count'] for s in self.inventory if s['item']['name'] == item.name])
        if count >= 10: return False
        return True

    def _add_to_inventory(self, item):
        # Capacity Check
        total_count = sum([s['count'] for s in self.inventory])
        if total_count >= 20:
             return False

        for slot in self.inventory:
            if slot['item']['name'] == item.name:
                slot['count'] += 1
                return True
        self.inventory.append({'item': item.to_dict(), 'count': 1})
        return True

    def eat_from_inventory(self) -> bool:
        for i, slot in enumerate(self.inventory):
            if "consumable" in slot['item']['tags']:
                slot['count'] -= 1
                self.nafs.hunger = max(0.0, self.nafs.hunger - 0.5)
                self.log_diary(f"Ate {slot['item']['name']}.")
                if slot['count'] <= 0: self.inventory.pop(i)
                return True
        return False
        
    def check_opportunistic_gathering(self, world):
        """
        If we are standing on something useful, pick it up (Free Action).
        """
        items = world.items_grid.get((self.x, self.y))
        if not items: return
        
        item = items[0] # Peek
        should_gather = False
        
        # Logic: Always gather construction mats
        if item.name in ["Wood", "Stone"]:
            should_gather = True
        
        # Logic: Gather food if hungry or inventory space exists
        elif "consumable" in item.tags:
            if self.nafs.hunger > 0.4 or self.attributes.personality_vector["Survival"] > 0.6:
                should_gather = True
                
        if should_gather:
            if sum(s['count'] for s in self.inventory) < 20:
                self.gather(world)

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
             # INCEST CHECK
             # Avoid if target is parent, child, or sibling (share parents)
             is_family = (target_id in self.attributes.parents or 
                          target_id in self.attributes.children or
                          (self.attributes.parents and target.attributes.parents and set(self.attributes.parents) & set(target.attributes.parents)))
             
             if is_family:
                  self.log_diary(f"{target.attributes.name} is my beloved kin.")
             elif self.attributes.gender != target.attributes.gender:
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
        """
        Determine Game Theory Strategy based on Personality with Stochastic Diversity.
        """
        p = self.attributes.personality_vector
        
        # Base Probabilities
        strategies = [
            GameStrategy.TIT_FOR_TAT.value,
            GameStrategy.GRIM_TRIGGER.value,
            GameStrategy.ALWAYS_COOPERATE.value,
            GameStrategy.ALWAYS_DEFECT.value,
            GameStrategy.RANDOM.value,
            GameStrategy.PAVLOV.value
        ]
        
        weights = [0.4, 0.1, 0.1, 0.1, 0.1, 0.2] # Default bias towards TFT and Pavlov
        
        # Personality Modifiers
        if p["Aggression"] > 0.6:
            # More likely to Defect/Grim
            weights = [0.2, 0.3, 0.05, 0.3, 0.05, 0.1]
        elif p["Altruism"] > 0.6:
            # More likely to Cooperate/TFT
            weights = [0.4, 0.05, 0.4, 0.0, 0.05, 0.1]
        elif p["Impulsivity"] > 0.7:
            # Random/Pavlov
            weights = [0.1, 0.05, 0.05, 0.1, 0.5, 0.2]
        elif p["Logic"] > 0.7:
             # Pavlov (Win-Stay, Lose-Switch) or TFT are logical
             weights = [0.4, 0.0, 0.0, 0.0, 0.0, 0.6]
             
        # Normalize weights
        total = sum(weights)
        norm_weights = [w/total for w in weights]
        
        self.attributes.strategy = np.random.choice(strategies, p=norm_weights)
        
    def get_public_state(self):
        """
        Returns observable state for other agents.
        """
        return {
            "id": self.id,
            "health": self.state.health,
            "hunger": self.nafs.hunger,
            "inventory": [slot['item']['name'] for slot in self.inventory], # List of item names
            "tribe": self.attributes.tribe_id
        }
        
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

    # --- TRADE & ECONOMY ---

    def initiate_trade(self, target, mode, world):
        """
        Calculates Offer/Request and asks Target.
        """
        # 1. Determine Needs & Surplus
        my_inventory = [s['item']['name'] for s in self.inventory]
        # target_inventory = target.get_public_state()['inventory'] # Use public perception
        
        offer_item = None
        request_item = None
        
        # Determine Surplus (More than 2 of something)
        counts = {}
        for i in my_inventory: counts[i] = counts.get(i, 0) + 1
        surplus = [k for k,v in counts.items() if v > 2]
        
        # Determine Need
        needs = []
        if self.nafs.hunger > 0.5: needs.append("Fruit") # Specifics
        if self.attributes.personality_vector["Conscientiousness"] > 0.5: # Builder
             if "Wood" not in my_inventory: needs.append("Wood")
        
        if mode == 'gift':
             if surplus:
                 # Offer random surplus
                 offer_item_name = np.random.choice(surplus)
                 # Find actual item object
                 for slot in self.inventory:
                     if slot['item']['name'] == offer_item_name:
                         offer_item = slot['item']
                         break
                 request_item = None # It's a gift
             else:
                 self.log_diary("Wanted to gift but had no surplus.")
                 return
                 
        elif mode == 'barter':
             # I need X, I offer Y
             if needs:
                 request_item_name = needs[0] # Simplistic
                 # Do they have it? (Based on perception)
                 # state = self.visible_agents_state.get(target.id)
                 # if not state or request_item_name not in str(state['inventory']):
                 #    return # Don't ask if they don't have it (or ask anyway?)
                 
                 # Find offer
                 if surplus:
                     offer_name = surplus[0]
                     for slot in self.inventory:
                         if slot['item']['name'] == offer_name:
                             offer_item = slot['item']
                             break
                 else:
                     # Begging? (Offer None)
                     offer_item = None
                     
                 # Construct Request (We don't have item object for request, just name)
                 request_item = request_item_name
             else:
                 self.log_diary("Wanted to trade but decided I need nothing.")
                 return

        # 2. Propose
        accepted = target.evaluate_trade(self, offer_item, request_item)
        
        if accepted:
            self.log_diary(f"Trade successful with {target.attributes.name} ({mode}).")
            self.execute_trade_transaction(target, offer_item, request_item, world)
            
            # Opinion Boost
            impact = 5 if mode == 'gift' else 1
            self.qalb.update_opinion(target.id, impact)
            target.qalb.update_opinion(self.id, impact)
        else:
            self.log_diary(f"Trade rejected by {target.attributes.name}.")
            if mode == 'barter':
                 self.qalb.update_opinion(target.id, -1)

    def evaluate_trade(self, proponent, offer_item, request_item_name) -> bool:
        """
        Decide whether to accept the trade using VALUE system.
        """
        # 1. Capacity Check
        current_count = sum([s['count'] for s in self.inventory])
        if current_count >= 20 and offer_item:
             # If I receive an item, do I have space?
             # Barter 1 for 1 is neutral. Gift receiving requires space.
             if not request_item_name: # Gift
                  return False # Full
             # Barter: 1 in, 1 out. OK.
        
        # 2. Can I fulfill request?
        if request_item_name:
            has_item = False
            for slot in self.inventory:
                if slot['item']['name'] == request_item_name:
                     has_item = True
                     break
            if not has_item: return False
            
        # 3. Value Calculation
        offer_val = offer_item['value'] if offer_item else 0
        
        # Get request value from BASE_VALUES via name
        from ..env.item import BASE_VALUES
        request_val = BASE_VALUES.get(request_item_name, 1) if request_item_name else 0
        
        # 4. Logic
        # Gift (Request is None): YES
        if request_item_name is None: return True
             
        # Begging (Offer is None): Friends only
        if offer_item is None:
             op = self.qalb.opinions.get(proponent.id, 0)
             return op > 20 or self.attributes.personality_vector["Altruism"] > 0.7
             
        # Barter
        # Critical Need Override
        my_needs = []
        if self.nafs.hunger > 0.5: my_needs.append("Fruit")
        if offer_item['name'] in my_needs: return True

        # Fair Value Check
        # Accept if Offer >= Request (or close enough/friend bonus)
        # Friend bonus: Discount 20%
        op = self.qalb.opinions.get(proponent.id, 0)
        discount = 0.8 if op > 10 else 1.0
        
        if offer_val >= (request_val * discount):
             return True
             
        return False
        
    def execute_trade_transaction(self, target, offer_item, request_item_name, world):
        """
        Moves items between inventories.
        """
        mode = 'gift' if not request_item_name else 'barter'
        
        # Move Offer to Target
        if offer_item:
             # Find in my inventory and remove 1
             for slot in self.inventory:
                 if slot['item']['name'] == offer_item['name']:
                     slot['count'] -= 1
                     if slot['count'] <= 0: self.inventory.remove(slot)
                     break
             
             # Add to Target (Manually respecting capacity? Target accepted so assumed ok)
             found = False
             for slot in target.inventory:
                 if slot['item']['name'] == offer_item['name']:
                     slot['count'] += 1
                     found = True
                     break
             if not found:
                 target.inventory.append({'item': offer_item, 'count': 1})
                 
        # Move Request to Me (from Target)
        if request_item_name:
             for slot in target.inventory:
                 if slot['item']['name'] == request_item_name:
                     slot['count'] -= 1
                     # Deep copy item dict before removing??
                     item_data = slot['item'].copy()
                     if slot['count'] <= 0: target.inventory.remove(slot)
                     
                     # Add to Me
                     found = False
                     for s in self.inventory:
                         if s['item']['name'] == request_item_name:
                             s['count'] += 1
                             found = True
                             break
                     if not found:
                         self.inventory.append({'item': item_data, 'count': 1})
                     break
        
        # Log to World
        world.log_trade(self, target, offer_item, request_item_name, mode)

    def combat_logic(self, target, world):
        """
        Executes an attack on the target.
        """
        # 1. Damage Calculation
        # Base damage based on Aggression and Strength (Energy/Health)
        damage = 0.1 + (self.attributes.aggression * 0.1)
        
        # Weapon Bonus
        has_weapon = False
        for slot in self.inventory:
            tags = slot['item'].get('tags', [])
            if "weapon" in tags:
                damage += 0.2
                has_weapon = True
                break
            elif "tool" in tags: # Axe/Pickaxe
                damage += 0.15
                break
        
        # 2. Defense
        # Reduced by target resilience/armor?
        # Target Health Update
        target.state.health -= damage
        
        # 3. Cost
        self.nafs.energy -= 0.05
        
        # 4. Social Fallout
        self.qalb.update_opinion(target.id, -20) # I hate you more
        target.qalb.update_opinion(self.id, -50) # Target hates me for attacking
        
        # 5. Logging
        weapon_str = " with weapon" if has_weapon else ""
        self.log_diary(f"Attacked {target.attributes.name}{weapon_str}!")
        target.log_diary(f"Attacked by {self.attributes.name}!")
        
        # Global Log if severe or kill
        if target.state.health <= 0:
            world.log_event(f"VIOLENCE: {self.attributes.name} KILLED {target.attributes.name}!")
        else:
             # Only log battles occasionally to avoid spam? Or always?
             # User requested "Agent x killed agent y", minimal violence notification.
             # Let's log significant hits?
             pass 

    def die(self, world):
        """
        Handles the death of the agent.
        """
        world.log_event(f"DEATH: {self.attributes.name} has died. (Age: {self.state.age_steps})")
        
        # 1. Drop Items? (Optional, let's keep it simple for now and delete them)
        # Maybe drop a "Corpse" item?
        
        # 2. Remove from Tribe
        if self.attributes.tribe_id:
             tribe = world.tribes.get(self.attributes.tribe_id)
             if tribe: tribe.remove_member(self.id)
             
        # 3. Remove from Partner
        if self.attributes.partner_id:
             partner = world.agents.get(self.attributes.partner_id)
             if partner: 
                 partner.attributes.partner_id = None
                 partner.log_diary(f"My love {self.attributes.name} has died. I am broken.")
                 partner.state.happiness = 0.0
                 
        # 4. Remove from World (This calls world.remove_agent usually, but we need to call it manually or let world handle it logic)
        # World.remove_agent isn't exposed yet, we need to modify agents dict directly or better, use a world method.
        # Let's assume world.agents.pop(self.id) is safe if we do it carefully.
        # Better: Mark as dead and let World clean up? Or direct removal.
        if self.id in world.agents:
            del world.agents[self.id]

    # --- HELPERS ---

    def distance_to(self, entity) -> float:
        return np.sqrt((self.x - entity.x)**2 + (self.y - entity.y)**2)

    def log_diary(self, entry: str):
        self.diary.append(f"[Life {self.ruh.soul.past_lives}] {entry}")
        if len(self.diary) > 50: self.diary.pop(0)

    def add_memory(self, desc: str, type="event", impact=0.0):
        self.ruh.soul.memories.append(Memory(type=type, description=desc, location=(self.x, self.y), time=self.state.age_steps, emotional_impact=impact))

    def calculate_job_title(self) -> str:
        """
        Derives a 'Job' or 'Class' based on Personality and Stats.
        """
        if self.attributes.is_prophet: return "Prophet"
        if self.attributes.leader_id == self.id: 
            return "Chieftain" if self.attributes.tribe_id else "Warlord"
        
        # Skill/Stat based
        p = self.attributes.personality_vector
        
        if p.get("Aggression", 0) > 0.8: return "Warrior"
        if p.get("Spirituality", 0) > 0.8: return "Shaman"
        if p.get("Curiosity", 0) > 0.8: return "Explorer"
        if p.get("Conscientiousness", 0) > 0.8: return "Builder"
        if p.get("Social", 0) > 0.8: return "Diplomat"
        
        return "Gatherer"

    def to_dict(self, world=None):
        """
        Serializer for Frontend/API.
        """
        # Resolve Names for UI
        def resolve_name(aid): 
            if not aid: return None
            if world:
                a = world.agents.get(aid)
                return a.attributes.name if a else "Unknown"
            return aid
            
        return {
            "id": self.id,
            "x": int(self.x),
            "y": int(self.y),
            "attributes": {
                **self.attributes.__dict__,
                "job": self.calculate_job_title(),
                "tribe_color": world.tribes[self.attributes.tribe_id].color if world and self.attributes.tribe_id and self.attributes.tribe_id in world.tribes else None,
                "partner_name": resolve_name(self.attributes.partner_id),
                "leader_name": resolve_name(self.attributes.leader_id),
                "parent_names": [resolve_name(pid) for pid in self.attributes.parents],
                "child_names": [resolve_name(cid) for cid in self.attributes.children]
            },
            "state": self.state.__dict__,
            "needs": { 
                "hunger": self.nafs.hunger,
                "energy": self.nafs.energy,
                "social": self.qalb.social,
                "fun": self.qalb.fun
            },
            "nafs": {k:v for k,v in self.nafs.__dict__.items() if k != 'agent'},
            "qalb": {k:v for k,v in self.qalb.__dict__.items() if k != 'agent' and k != 'brain'}, 
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
            "tribe_id": self.attributes.tribe_id,
            "tribe_name": world.tribes[self.attributes.tribe_id].name if world and self.attributes.tribe_id and self.attributes.tribe_id in world.tribes else "Nomad",
            "tribe_goal": world.tribes[self.attributes.tribe_id].goal if world and self.attributes.tribe_id and self.attributes.tribe_id in world.tribes else "wander",
            "tribe_harmony": world.tribes[self.attributes.tribe_id].calculate_harmony(world) if world and self.attributes.tribe_id and self.attributes.tribe_id in world.tribes else 50.0,
            "generation": self.attributes.generation,
            "brain": self.brain.to_dict()
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
        

    def join_tribe(self, tribe_id, world):
        """
        Handles the logic of joining a tribe, including Chief Transition.
        """
        if self.attributes.tribe_id == tribe_id: return
        
        new_tribe = world.tribes.get(tribe_id)
        if not new_tribe: return
        
        old_tribe_id = self.attributes.tribe_id
        
        # 1. Chief Transition Check
        # Am I a leader of a different tribe?
        if self.attributes.leader_id == self.id and len(self.attributes.followers) > 0:
             self.log_diary(f"I, Chief {self.attributes.name}, am submitting to {new_tribe.name}.")
             
             # Option A: Migrate whole tribe (Merge)
             # Move all followers to new tribe
             # Create a copy of the list to iterate safely
             followers_to_migrate = list(self.attributes.followers)
             for follower_id in followers_to_migrate:
                 follower = world.agents.get(follower_id)
                 if follower:
                     # Recursive but safe if logic holds
                     follower.join_tribe(tribe_id, world) 
                     follower.attributes.leader_id = new_tribe.leader_id 
             
        # 2. Leave Old Tribe
        if old_tribe_id and old_tribe_id in world.tribes:
            world.tribes[old_tribe_id].remove_member(self.id)
            
        # 3. Join New Tribe
        self.attributes.tribe_id = tribe_id
        self.attributes.leader_id = new_tribe.leader_id
        new_tribe.add_member(self.id)
        
        # 4. Update New Leader's Followers list
        if new_tribe.leader_id:
             leader = world.agents.get(new_tribe.leader_id)
             if leader and self.id not in leader.attributes.followers:
                 leader.attributes.followers.append(self.id)
                 
        self.log_diary(f"Joined tribe: {new_tribe.name}")


