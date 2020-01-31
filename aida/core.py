from typing import List, Union
import random

PrimaryType = Union[str, int, float]
ValidType = Union['AidaObj', PrimaryType]


class AidaObj(object):
    def render(self) -> 'ValidType':
        raise NotImplementedError()

    def __add__(self, other) -> 'Node':
        return Node([self, other])


def render(aida_obj: ValidType):
    if isinstance(aida_obj, AidaObj):
        return render(aida_obj.render())
    elif isinstance(aida_obj, (int, float, str)):
        return str(aida_obj)
    else:
        raise Exception(f'Unexpected obj {aida_obj}')


class Node(AidaObj):
    def __init__(self, items: List[ValidType]) -> None:
        self.items = items

    def render(self) -> str:
        return ' '.join(render(obj) for obj in self.items)


class Const(AidaObj):
    def __init__(self, obj: ValidType) -> None:
        self.obj = obj

    def render(self) -> ValidType:
        return self.obj


class Slot(AidaObj):
    def __init__(self, name: str = None) -> None:
        self.name = name
        self.value = None

    def assign(self, val: ValidType) -> 'Slot':
        self.value = val
        return self

    def render(self) -> ValidType:
        assert self.value is not None
        return self.value


class Choices(AidaObj):
    def __init__(self, items: List[ValidType], seed=None) -> None:
        self.items = items
        if seed is not None:
            random.seed(seed)

    def render(self) -> ValidType:
        return random.choice(self.items)
