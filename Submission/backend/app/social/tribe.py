from dataclasses import dataclass, field
from typing import List, Dict, Optional
import uuid
import numpy as np

@dataclass
class Tribe:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Unnamed Tribe"
    leader_id: Optional[str] = None
    members: List[str] = field(default_factory=list)
    color: str = "#ffffff"
    goal: str = "wander"
    goal: str = "wander"
    enemies: List[str] = field(default_factory=list) # List of Enemy Tribe IDs
    resources: Dict[str, int] = field(default_factory=lambda: {"food": 0, "wood": 0, "stone": 0})
    
    def __post_init__(self):
        # Assign random color
        if self.color == "#ffffff":
            self.color = f"#{np.random.randint(0, 0xFFFFFF):06x}"

    def set_leader(self, agent_id: str):
        self.leader_id = agent_id
        if agent_id not in self.members:
            self.members.append(agent_id)

    def add_member(self, agent_id: str):
        if agent_id not in self.members:
            self.members.append(agent_id)

    def remove_member(self, agent_id: str):
        if agent_id in self.members:
            self.members.remove(agent_id)
        if self.leader_id == agent_id:
            self.leader_id = None # Anarchy!

    def set_goal(self, goal: str):
        self.goal = goal

    def assess_needs(self):
        """
        Determines the tribe's current goal based on resource levels.
        """
        # 1. Food Security (Highest Priority)
        # Goal: 5 food per member
        if self.resources["food"] < len(self.members) * 5:
            self.goal = "gather_food"
            return

        # 2. Material Security
        if self.resources["wood"] < 10:
            self.goal = "gather_wood"
            return
            
        if self.resources["stone"] < 10:
            self.goal = "gather_stone"
            return
            
        # 3. Expansion
        self.goal = "build_home" # Placeholder for future logic
        
    def calculate_harmony(self, world) -> float:
        """
        Calculates the average opinion members have of each other and the leader.
        Returns a score between 0 and 100.
        """
        if not self.members:
            return 100.0
            
        total_score = 0
        count = 0
        
        # Check opinions between all members
        for member_id in self.members:
            agent = world.agents.get(member_id)
            if not agent: continue
            
            # Opinion of Leader
            if self.leader_id and self.leader_id != member_id:
                op_leader = agent.qalb.opinions.get(self.leader_id, 0)
                total_score += op_leader
                count += 1
            
            # General cohesion (sample a few peers to save perf)
            # just checks leader for now to keep it O(N) instead of O(N^2)
        
        if count == 0:
            return 50.0 # Neutral
            
        avg_opinion = total_score / count
        # Map opinion (-100 to 100) to Harmony (0 to 100)
        # 0 opinion -> 50 harmony
        harmony = (avg_opinion + 100) / 2
        return max(0.0, min(100.0, harmony))

    def declare_war(self, target_tribe_id: str, world):
        if target_tribe_id not in self.enemies:
            self.enemies.append(target_tribe_id)
            # Log
            target = world.tribes.get(target_tribe_id)
            target_name = target.name if target else "Unknown Tribe"
            world.log_event(f"WAR: Tribe {self.name} has declared war on {target_name}!")

    def to_dict(self, world=None):
        harmony = 0.0
        if world:
            harmony = self.calculate_harmony(world)
            
        return {
            "id": self.id,
            "name": self.name,
            "leader_id": self.leader_id,
            "member_count": len(self.members),
            "color": self.color,
            "goal": self.goal,
            "resources": self.resources,
            "harmony": harmony
        }
