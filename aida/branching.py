from typing import cast

from .choices import Choices
from .core import (
    Ctx, Empty, Node, Operation, ValidType, _update_ctx, to_node)

__all__ = ['Branch', 'create_alt', 'create_ref']


class Branch(Node):
    def __init__(self, cond: Node, left: ValidType, right: ValidType = None) -> None:
        self.cond = cond
        self.left = to_node(left)
        self.right = to_node(right or Empty)

    def __hash__(self) -> int:
        return hash((self.__class__.__name__, self.cond, self.left, self.right))

    def __repr__(self) -> str:
        return f'Branch({self.cond} ? {self.left} : {self.right})'

    def render(self, ctx: Ctx) -> ValidType:
        alternative = self.left if cast(
            Operation, self.cond.value).eval(ctx) else self.right
        ret = alternative.render(ctx)
        return _update_ctx(ctx, self, ret)


def create_alt(left: ValidType, right: ValidType = None) -> Branch:
    left_ = to_node(left)
    return Branch(~left_.in_ctx(), left_, right or Empty)


def create_ref(absolute, *alts: ValidType) -> Branch:
    return create_alt(left=absolute, right=Choices(*alts))
