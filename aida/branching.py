from typing import cast

from .choices import Choices
from .core import (
    Ctx, Empty, Node, Operation, ValidType, Var, _update_ctx, to_node)

__all__ = ['Branch', 'create_alt', 'create_ref', 'create_match', 'create_once']


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
        cond_eval = cast(Operation, self.cond.value).render(
            ctx) if isinstance(self.cond.value, Operation) else self.cond.value
        alternative = self.left if cond_eval else self.right
        ret = alternative.render(ctx)
        return _update_ctx(ctx, self, ret)


def create_alt(left: ValidType, right: ValidType = None) -> Branch:
    left_ = to_node(left)
    return Branch(~left_.in_ctx(), left_, right or Empty)


def create_ref(absolute, *alts: ValidType) -> Branch:
    return create_alt(left=absolute, right=Choices(*alts))


def create_once(node: ValidType) -> Branch:
    return create_alt(node, Empty)


def create_match(label_var: Var, default: ValidType = None, **matches) -> Node:
    b = to_node(default or Empty)
    for label_value, output in matches.items():
        b = Branch(label_var == label_value, output, b)
    return b
