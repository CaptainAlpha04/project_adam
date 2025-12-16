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
        
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "leader_id": self.leader_id,
            "member_count": len(self.members),
            "color": self.color,
            "goal": self.goal,
            "resources": self.resources
        }
