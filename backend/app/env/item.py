from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class Item:
    id: str
    name: str
    weight: float
    hardness: float
    durability: float
    tags: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    value: int = 1 # Default value

    def __post_init__(self):
        # Assign default value if generic
        if self.value == 1 and self.name in BASE_VALUES:
            self.value = BASE_VALUES[self.name]

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "weight": self.weight,
            "hardness": self.hardness,
            "durability": self.durability,
            "tags": self.tags,
            "durability": self.durability,
            "tags": self.tags,
            "properties": self.properties,
            "value": self.value
        }

# Simple Recipe System
# Output Item Name -> List of required tags/names
RECIPES = {
    "Hammer": {"components": ["stick", "stone"], "tags": ["tool", "crushing"]},
    "Axe": {"components": ["stick", "sharp_stone"], "tags": ["tool", "cutting"]},
    "Pickaxe": {"components": ["stick", "sharp_stone", "stone"], "tags": ["tool", "mining"]},
    "Spear": {"components": ["long_stick", "sharp_stone"], "tags": ["weapon", "piercing"]},
    "Stone Block": {"components": ["stone"], "tags": ["material", "building"]},
    "Wall": {"components": ["stone_block", "stone_block"], "tags": ["building", "defense"]},
    "Door": {"components": ["stone_block", "wood"], "tags": ["building", "access"]},
}

BASE_VALUES = {
    "Wood": 2,
    "Stone": 2, 
    "Fruit": 5, # Food is valuable
    "Meat": 8,
    "Stick": 1,
    "Sharp Stone": 3,
    "Axe": 15, # Processed items + Utility
    "Pickaxe": 15,
    "Stone Block": 5,
    "Wall": 12,
    "Diamond": 50, # Rare
    "Gold": 25
}
