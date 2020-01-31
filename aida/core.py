from typing import List, Union
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
        return Node([self, other])

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


class Node(AidaObj):
    def __init__(self, items: List[ValidType]) -> None:
        self.items = items

    def __hash__(self) -> int:
        return hash(tuple(self.items))

    def render(self, ctx) -> str:
        ret = ' '.join(render(obj, ctx) for obj in self.items)
        ctx.add(self)
        return ret


class Const(AidaObj):
    def __init__(self, obj: ValidType) -> None:
        self.obj = obj

    def __hash__(self) -> int:
        return hash(self.obj)

    def render(self, ctx) -> ValidType:
        ctx.add(self)
        return self.obj


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
        ctx.add(self)
        return self.value


class Choices(AidaObj):
    def __init__(self, items: List[ValidType], seed=None) -> None:
        self.items = items
        if seed is not None:
            random.seed(seed)

    def __hash__(self) -> int:
        return hash(tuple(self.items))

    def render(self, ctx) -> ValidType:
        ret = random.choice(self.items)
        ctx.add(ret)
        return ret


class Alt(AidaObj):
    def __init__(self, main: ValidType, alt: ValidType = None) -> None:
        self.main = main
        self.alt = alt or Empty

    def __hash__(self) -> int:
        return hash((self.main, self.alt))

    def render(self, ctx) -> ValidType:
        valid_obj = self.alt if ctx.contains(self.main) else self.main
        ctx.add(valid_obj)
        return valid_obj.render(ctx) if isinstance(valid_obj, AidaObj) else valid_obj


def create_ref(absolute: ValidType, alts: List[ValidType]) -> Alt:
    return Alt(main=absolute, alt=Choices(alts))
