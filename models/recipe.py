from dataclasses import dataclass
from typing import Dict, List

@dataclass
class Recipe:
    name: str
    ingredients: List[str]
    steps: List[str]

def recipe_builder(modeled_dic) -> Recipe:
    r: Dict[str, str] = modeled_dic['output']
    return Recipe(name=r['title'],
                  ingredients=r['ingrs'],
                  steps=r['recipe'])
