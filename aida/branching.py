from typing import cast

from .choices import Choices
from .core import (
    Ctx, Empty, Operand, Operation, ValidType, _update_ctx, to_operand)

__all__ = ['Branch', 'create_alt', 'create_ref']


class Branch(Operand):
    def __init__(self, cond: Operand, left: ValidType, right: ValidType = None) -> None:
        self.cond = cond
        self.left = to_operand(left)
        self.right = to_operand(right or Empty)

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
    left_ = to_operand(left)
    return Branch(~left_.in_ctx(), left_, right or Empty)


def create_ref(absolute, *alts: ValidType) -> Branch:
    return create_alt(left=absolute, right=Choices(*alts))
