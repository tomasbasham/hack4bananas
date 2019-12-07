from dataclasses import dataclass
from typing import List

@dataclass
class Recipe:
    name: str
    ingredients: List[str]
    steps: List[str]
