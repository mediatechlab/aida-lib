from typing import List, Union, cast
import random

PrimaryType = Union[str, int, float]
ValidType = Union['AidaObj', PrimaryType]


class Ctx(object):
    def __init__(self) -> None:
        self.store = set()

    def contains(self, aida_obj: ValidType) -> bool:
        return hash(aida_obj) in self.store

    def add(self, aida_obj: ValidType) -> 'Ctx':
        self.store.add(hash(aida_obj))
        return self


class AidaObj(object):
    def render(self, ctx: Ctx) -> 'ValidType':
        raise NotImplementedError()

    def __add__(self, other) -> 'Node':
        return Node([self, other], sep=' ')

    def __mul__(self, other) -> 'Node':
        return Node([self, other], sep='')

    def __hash__(self) -> int:
        raise NotImplementedError()


def render(aida_obj: ValidType, ctx: Ctx = None):
    ctx = ctx or Ctx()
    if isinstance(aida_obj, AidaObj):
        return render(aida_obj.render(ctx), ctx)
    elif isinstance(aida_obj, (int, float, str)):
        return str(aida_obj)
    else:
        raise Exception(f'Unexpected obj {aida_obj}')


def _update_ctx(ctx: Ctx, *items: ValidType) -> ValidType:
    for item in items:
        ctx.add(item)
    return items[-1]


class Node(AidaObj):
    def __init__(self, items: List[ValidType], sep=' ') -> None:
        self.items = items
        self.sep = sep

    def __hash__(self) -> int:
        return hash(tuple(self.items))

    def render(self, ctx) -> str:
        ret = self.sep.join(render(obj, ctx) for obj in self.items)
        return cast(str, _update_ctx(ctx, self, ret))


class Const(AidaObj):
    def __init__(self, obj: ValidType) -> None:
        self.obj = obj

    def __hash__(self) -> int:
        return hash(self.obj)

    def render(self, ctx) -> ValidType:
        return _update_ctx(ctx, self, self.obj)


Empty = Const('')


class Slot(AidaObj):
    def __init__(self, name: str = None) -> None:
        self.name = name
        self.value = None

    def __hash__(self) -> int:
        return hash(self.name)

    def assign(self, val: ValidType) -> 'Slot':
        self.value = val
        return self

    def render(self, ctx) -> ValidType:
        assert self.value is not None
        return _update_ctx(ctx, self, self.value)


class Choices(AidaObj):
    def __init__(self, items: List[ValidType], seed=None) -> None:
        self.items = items
        if seed is not None:
            random.seed(seed)

    def __hash__(self) -> int:
        return hash(tuple(self.items))

    def render(self, ctx) -> ValidType:
        ret = random.choice(self.items)
        return _update_ctx(ctx, self, ret)


class Alt(AidaObj):
    def __init__(self, main: ValidType, alt: ValidType = None) -> None:
        self.main = main
        self.alt = alt or Empty

    def __hash__(self) -> int:
        return hash((self.main, self.alt))

    def render(self, ctx) -> ValidType:
        valid_obj = self.alt if ctx.contains(self.main) else self.main
        ret = valid_obj.render(ctx) if isinstance(
            valid_obj, AidaObj) else valid_obj
        return _update_ctx(ctx, valid_obj, self, ret)


def create_ref(absolute: ValidType, alts: List[ValidType]) -> Alt:
    return Alt(main=absolute, alt=Choices(alts))


class Enumeration(AidaObj):
    def __init__(self, aida_objs: List[ValidType], lang='en-US') -> None:
        self.aida_objs = aida_objs
        assert lang == 'en-US', f'Unsupported language {lang}'

    def __hash__(self) -> int:
        return hash(tuple(self.aida_objs))

    def _render(self, ctx: Ctx, n_items: int, items: List[ValidType]) -> ValidType:
        if len(items) == 0:
            return Empty
        elif len(items) == 1:
            return Const(items[0])
        elif len(items) == 2:
            c = Const(items[0])
            return (c + 'and' if n_items == 2 else c * ', and') + Const(items[1])
        else:
            return Const(items[0]) * ',' + self._render(ctx, n_items, items[1:])

    def render(self, ctx: Ctx) -> ValidType:
        ret = self._render(ctx, len(self.aida_objs), self.aida_objs)
        return _update_ctx(ctx, self, ret)
