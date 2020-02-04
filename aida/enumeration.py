from typing import List

from .core import Ctx, Empty, Node, ValidType, _update_ctx, to_node

__all__ = ['Enumeration']


class Enumeration(Node):
    def __init__(self, *aida_objs: ValidType, lang='en-US') -> None:
        self.aida_objs = tuple(map(to_node, aida_objs))
        assert lang == 'en-US', f'Unsupported language {lang}'

    def __hash__(self) -> int:
        return hash(self.aida_objs)

    def __repr__(self) -> str:
        return f'Enumeration({self.aida_objs})'

    def _render(self, ctx: Ctx, n_items: int, items: List[Node]):
        if len(items) == 0:
            return Empty

        elif len(items) == 1:
            return items[0].render(ctx)

        elif len(items) == 2:
            item0 = items[0].render(ctx)
            return ((item0 + ' and ') if n_items == 2 else (item0 + ', and ')) + items[1].render(ctx)

        else:
            return (items[0].render(ctx) + ', ') + self._render(ctx, n_items, items[1:])

    def render(self, ctx: Ctx) -> ValidType:
        ret = self._render(ctx, len(self.aida_objs), list(self.aida_objs))
        return _update_ctx(ctx, self, ret)
