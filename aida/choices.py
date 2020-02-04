import random

from .core import Ctx, Node, ValidType, _update_ctx, to_node


__all__ = ['Choices']


class Choices(Node):
    def __init__(self, *items: ValidType, seed=None) -> None:
        self.items = tuple(map(to_node, items))
        if seed is not None:
            random.seed(seed)

    def __hash__(self) -> int:
        return hash((self.__class__.__name__, self.items))

    def __repr__(self) -> str:
        return f'Choices({self.items})'

    def render(self, ctx: Ctx) -> ValidType:
        ret = random.choice(self.items)
        return _update_ctx(ctx, self, ret)
