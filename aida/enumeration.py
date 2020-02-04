from typing import Tuple, cast

from .core import AidaObj, Ctx, Empty, ValidType, _update_ctx, to_aida_obj

__all__ = ['Enumeration']


class Enumeration(AidaObj):
    def __init__(self, *aida_objs: ValidType, lang='en-US') -> None:
        self.aida_objs = tuple(map(to_aida_obj, aida_objs))
        assert lang == 'en-US', f'Unsupported language {lang}'

    def __hash__(self) -> int:
        return hash(self.aida_objs)

    def __repr__(self) -> str:
        return f'Enumeration({self.aida_objs})'

    def _render(self, ctx: Ctx, n_items: int, items: Tuple[AidaObj]) -> AidaObj:
        if len(items) == 0:
            return Empty

        elif len(items) == 1:
            return items[0]

        elif len(items) == 2:
            return (items[0] | 'and' if n_items == 2 else items[0] + ', and') | items[1]

        else:
            return items[0] + ',' | self._render(ctx, n_items, items[1:])

    def render(self, ctx: Ctx) -> AidaObj:
        ret = self._render(ctx, len(self.aida_objs), self.aida_objs)
        return cast(AidaObj, _update_ctx(ctx, self, ret))
