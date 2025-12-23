from dataclasses import dataclass, field
from typing import List, Optional
from .item import Item

@dataclass
class Tile:
    x: int
    y: int
    terrain_type: str  # 'water', 'grass', 'forest', 'stone', 'sand'
    items: List[Item] = field(default_factory=list)
    agent_id: Optional[str] = None
    resource_amount: float = 1.0  # For renewable resources like trees/food

    def to_dict(self):
        return {
            "x": self.x,
            "y": self.y,
            "terrain_type": self.terrain_type,
            "items": [item.to_dict() for item in self.items],
            "agent_id": self.agent_id,
            "resource_amount": self.resource_amount
        }
