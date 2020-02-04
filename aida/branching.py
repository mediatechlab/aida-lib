from typing import List, cast

from .choices import Choices
from .core import (
    AidaObj, Ctx, Empty, Operand, ValidType, _update_ctx, to_aida_obj,
    to_operand)

__all__ = ['Branch', 'create_alt', 'create_ref']


class Branch(AidaObj):
    def __init__(self, cond: Operand, left: ValidType, right: ValidType = None) -> None:
        self.cond = cond
        self.left = to_operand(left)
        self.right = to_aida_obj(right or Empty)

    def __hash__(self) -> int:
        return hash((self.__class__.__name__, self.cond, self.left, self.right))

    def __repr__(self) -> str:
        return f'Branch({self.cond} ? {self.left} : {self.right})'

    def render(self, ctx: Ctx) -> AidaObj:
        alternative = self.left if self.cond.value.eval() else self.right
        ret = alternative.render(ctx)
        return cast(AidaObj, _update_ctx(ctx, self, ret))


def create_alt(ctx: Ctx, left: ValidType, right: ValidType = None) -> Branch:
    left_ = to_operand(left)
    return Branch(~left_.in_ctx(ctx), left_, right or Empty)


def create_ref(ctx: Ctx, absolute, alts: List[ValidType]) -> Branch:
    return create_alt(ctx, left=absolute, right=Choices(alts))
