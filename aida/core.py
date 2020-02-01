from typing import List, Tuple, Union, cast
import operator
import random

__all__ = ['Ctx', 'render', 'Const', 'Var',
           'Empty', 'Choices', 'Alt', 'Enumeration']

PrimaryType = Union[str, int, float]
ValidType = Union['AidaObj', PrimaryType]


def to_aida_obj(obj: ValidType) -> 'AidaObj':
    if isinstance(obj, AidaObj):
        return obj
    else:
        return Const(obj)


class Ctx(object):
    def __init__(self) -> None:
        self.store = set()

    def contains(self, aida_obj: 'AidaObj') -> bool:
        return hash(aida_obj) in self.store

    def add(self, aida_obj: 'AidaObj') -> 'Ctx':
        self.store.add(hash(aida_obj))
        return self


class AidaObj(object):
    def render(self, ctx: Ctx) -> 'AidaObj':
        raise NotImplementedError()

    def __or__(self, other) -> 'Node':
        return Node([self, other], sep=' ')

    def __add__(self, other) -> 'Node':
        return Node([self, other], sep='')


def render(aida_obj: ValidType, ctx: Ctx = None) -> Union[AidaObj, str]:
    ctx = ctx or Ctx()
    if isinstance(aida_obj, AidaObj):
        return render(aida_obj.render(ctx), ctx)
    else:
        return str(aida_obj)


def _update_ctx(ctx: Ctx, *items: ValidType) -> ValidType:
    for item in items:
        if isinstance(item, AidaObj):
            ctx.add(item)
    return items[-1]


class Node(AidaObj):
    def __init__(self, items: List[ValidType], sep=' ') -> None:
        self.items = tuple(map(to_aida_obj, items))
        self.sep = sep

    def __hash__(self) -> int:
        return hash(self.items)

    def render(self, ctx: Ctx) -> str:
        ret = self.sep.join(render(obj, ctx) for obj in self.items)
        return cast(str, _update_ctx(ctx, self, ret))


class Const(AidaObj):
    def __init__(self, obj: PrimaryType) -> None:
        self.obj = str(obj)

    def __hash__(self) -> int:
        return hash(self.obj)

    def render(self, ctx) -> str:
        return cast(str, _update_ctx(ctx, self, self.obj))


Empty = Const('')


class Var(AidaObj):
    def __init__(self, name: str = None) -> None:
        self.name = name
        self.value = None

    def __hash__(self) -> int:
        return hash((self.__class__.__name__, self.name))

    def assign(self, val: ValidType) -> 'Var':
        self.value = to_aida_obj(val)
        return self

    def render(self, ctx) -> AidaObj:
        assert self.value is not None
        return cast(AidaObj, _update_ctx(ctx, self, self.value))


class Choices(AidaObj):
    def __init__(self, items: List[ValidType], seed=None) -> None:
        self.items = tuple(map(to_aida_obj, items))
        if seed is not None:
            random.seed(seed)

    def __hash__(self) -> int:
        return hash((self.__class__.__name__, self.items))

    def render(self, ctx) -> AidaObj:
        ret = random.choice(self.items)
        return cast(AidaObj, _update_ctx(ctx, self, ret))


class Alt(AidaObj):
    def __init__(self, main: ValidType, alt: ValidType = None) -> None:
        self.main = to_aida_obj(main)
        self.alt = to_aida_obj(alt or Empty)

    def __hash__(self) -> int:
        return hash((self.__class__.__name__, self.main, self.alt))

    def render(self, ctx) -> AidaObj:
        valid_obj = self.alt if ctx.contains(self.main) else self.main
        ret = valid_obj.render(ctx) if isinstance(
            valid_obj, AidaObj) else valid_obj
        return cast(AidaObj, _update_ctx(ctx, valid_obj, self, ret))


def create_ref(absolute: ValidType, alts: List[ValidType]) -> Alt:
    return Alt(main=absolute, alt=Choices(alts))


class Enumeration(AidaObj):
    def __init__(self, aida_objs: List[ValidType], lang='en-US') -> None:
        self.aida_objs = tuple(map(to_aida_obj, aida_objs))
        assert lang == 'en-US', f'Unsupported language {lang}'

    def __hash__(self) -> int:
        return hash(self.aida_objs)

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
