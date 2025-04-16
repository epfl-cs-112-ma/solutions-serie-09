# Rappel : sur papier, les `import` ne sont pas requis.
# De plus, toutes les `def __init__` qui sont marquées avec "init standard"
# n'ont pas besoin d'être écrites sur papier ; la mention "... # init standard"
# suffit.

# N'oubliez pas aussi qu'il y a beaucoup de solutions possibles. Cette
# version-ci n'est pas forcément meilleure q'une autre.

from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Final, Mapping, Sequence

class ResourceCategory(Enum):
    MATERIAL = auto()
    GOODS = auto()

@dataclass(frozen=True)
class Resource:
    name: str
    category: ResourceCategory

class Side(Enum):
    LEFT = auto()
    RIGHT = auto()

class Card:
    name: Final[str]
    required_resources: Final[tuple[Resource, ...]]
    chained_from: Final[str | None]

    # ... init standard
    def __init__(
        self,
        name: str,
        required_resources: tuple[Resource, ...],
        chained_from: str | None,
    ) -> None:
        self.name = name
        self.required_resources = required_resources
        self.chained_from = chained_from

    def production(self) -> Mapping[Resource, int]:
        return {}

    def has_discount_for(self, category: ResourceCategory, side: Side) -> bool:
        return False

class ProductionCard(Card):
    produced_resource: Final[Resource]
    amount: Final[int]

    # ... init standard
    def __init__(
        self,
        name: str,
        required_resources: tuple[Resource, ...],
        chained_from: str | None,
        produced_resource: Resource,
        amount: int,
    ) -> None:
        super().__init__(name, required_resources, chained_from)
        self.produced_resource = produced_resource
        self.amount = amount

    def production(self) -> Mapping[Resource, int]:
        return {self.produced_resource: self.amount}

class CommercialCard(Card):
    category: Final[ResourceCategory]
    sides: Final[frozenset[Side]]

    # ... init standard
    def __init__(
        self,
        name: str,
        required_resources: tuple[Resource, ...],
        chained_from: str | None,
        category: ResourceCategory,
        sides: frozenset[Side],
    ) -> None:
        super().__init__(name, required_resources, chained_from)
        self.category = category
        self.sides = sides

    def has_discount_for(self, category: ResourceCategory, side: Side) -> bool:
        return category == self.category and side in self.sides

class Production:
    __pool: Final[dict[Resource, int]]

    def __init__(self, initial_pool: Mapping[Resource, int]) -> None:
        self.__pool = dict(initial_pool)

    def has(self, resource: Resource) -> bool:
        return self.__pool.get(resource, 0) > 0

    @abstractmethod
    def cost_for(self, resource: Resource) -> int: ...

    def consume(self, resource: Resource) -> None:
        assert self.has(resource)
        self.__pool[resource] -= 1

class OwnProduction(Production):
    def cost_for(self, resource: Resource) -> int:
        return 0

class NeighborProduction(Production):
    __side: Final[Side]
    __cards: Final[Sequence[Card]]

    def __init__(self, initial_pool: Mapping[Resource, int], side: Side, cards: Sequence[Card]) -> None:
        super().__init__(initial_pool)
        self.__side = side
        self.__cards = cards

    def cost_for(self, resource: Resource) -> int:
        if any([card.has_discount_for(resource.category, self.__side) for card in self.__cards]):
            return 1
        else:
            return 0

def try_consume_resource(resource: Resource, productions: list[Production]) -> int | None:
    offers = [(prod, prod.cost_for(resource)) for prod in productions if prod.has(resource)]
    if len(offers) > 0:
        best_offer_prod, best_offer_cost = min(offers, key=lambda offer: offer[1])
        best_offer_prod.consume(resource)
        return best_offer_cost
    else:
        return None

@dataclass(frozen=True)
class Civilization:
    name: str # we don't really use this
    produced_resource: Resource

class Player:
    civilization: Final[Civilization]
    built_cards: Final[list[Card]]

    def __init__(self, civilization: Civilization) -> None:
        self.civilization = civilization
        self.built_cards = []

    def production(self) -> Mapping[Resource, int]:
        # start with the production of the civilization
        result = {self.civilization.produced_resource: 1}
        # then add the productions of the built cards
        for card in self.built_cards:
            for resource, amount in card.production().items():
                result[resource] = result.get(resource, 0) + amount
        return result

    def __can_build_chaining(self, card: Card) -> bool:
        return any([c.name == card.chained_from for c in self.built_cards])

    def __non_chaining_build_cost(self, card: Card, left_neighbor: Player, right_neighbor: Player) -> int | None:
        # Create new productions from myself and from my neighbors
        my_prod = OwnProduction(self.production())
        left_prod = NeighborProduction(left_neighbor.production(), Side.LEFT, self.built_cards)
        right_prod = NeighborProduction(right_neighbor.production(), Side.RIGHT, self.built_cards)
        prods = [my_prod, left_prod, right_prod]

        # Try to consume each required resource
        # Add up the cost of consuming each resource
        total_cost = 0
        for resource in card.required_resources:
            cost = try_consume_resource(resource, prods)
            if cost is None:
                # There is no way we can obtain that resource, so we cannot build that card
                return None
            total_cost += cost

        return total_cost

    def build_cost(self, card: Card, left_neighbor: Player, right_neighbor: Player) -> int | None:
        if self.__can_build_chaining(card):
            return 0 # it's free
        else:
            return self.__non_chaining_build_cost(card, left_neighbor, right_neighbor)
