from typing import List, Tuple, Union, cast
import operator
import random

__all__ = ['Ctx', 'render', 'Const', 'Var', 'Empty',
           'Choices', 'Alt', 'Enumeration', 'Branch']

PrimaryType = Union[str, int, float, bool]
ValidType = Union['AidaObj', PrimaryType]


def to_aida_obj(obj: ValidType) -> 'AidaObj':
    return obj if isinstance(obj, AidaObj) else Const(obj)


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


class Operand(object):
    def __init__(self, value=None) -> None:
        self.value = value

    def __hash__(self) -> int:
        return hash(self.value)

    def __and__(self, other) -> 'Operand':
        return Operand(Operation('and_', self, other))

    def __gt__(self, other) -> 'Operand':
        return Operand(Operation('gt', self, other))

    def __ge__(self, other) -> 'Operand':
        return Operand(Operation('ge', self, other))

    def __lt__(self, other) -> 'Operand':
        return Operand(Operation('lt', self, other))

    def __le__(self, other) -> 'Operand':
        return Operand(Operation('le', self, other))

    def __eq__(self, other) -> 'Operand':
        return Operand(Operation('eq', self, other))

    def __ne__(self, other) -> 'Operand':
        return Operand(Operation('ne', self, other))


class Operation(object):
    def __init__(self, op, *operands: Operand) -> None:
        self.op = op
        self.operands = operands

    def __hash__(self) -> int:
        return hash((self.op, self.operands))

    @staticmethod
    def _unwrap(item):
        if isinstance(item, Operation):
            return Operation._unwrap(item.eval())
        elif isinstance(item, Operand):
            return Operation._unwrap(item.value)
        else:
            return item

    def eval(self):
        values = [self._unwrap(opr) for opr in self.operands]

        if self.op in ('gt', 'ge', 'lt', 'le', 'eq', 'ne', 'and_'):
            assert len(self.operands) == 2
        else:
            assert len(self.operands) == 1

        return getattr(operator, self.op)(*values)


class Const(AidaObj, Operand):
    def __init__(self, value: PrimaryType) -> None:
        super().__init__(value)

    def __hash__(self) -> int:
        return hash(self.value)

    def render(self, ctx) -> str:
        return cast(str, _update_ctx(ctx, self, str(self.value)))


Empty = Const('')


class Branch(AidaObj):
    def __init__(self, cond: Operand, left: ValidType, right: ValidType = Empty) -> None:
        self.cond = cond
        self.left = to_aida_obj(left)
        self.right = to_aida_obj(right)

    def __hash__(self) -> int:
        return hash((self.__class__.__name__, self.cond, self.left, self.right))

    def render(self, ctx: Ctx) -> AidaObj:
        alternative = self.left if self.cond.value.eval() else self.right
        ret = alternative.render(ctx)
        return cast(AidaObj, _update_ctx(ctx, self, ret))


class Var(AidaObj, Operand):
    def __init__(self, name: str = None) -> None:
        super().__init__()
        self.name = name

    def __hash__(self) -> int:
        return hash((self.__class__.__name__, self.name))

    def assign(self, value: PrimaryType) -> 'Var':
        self.value = value
        return self

    def render(self, ctx: Ctx) -> str:
        assert self.value is not None
        return cast(str, _update_ctx(ctx, self, str(self.value)))


class Choices(AidaObj):
    def __init__(self, items: List[ValidType], seed=None) -> None:
        self.items = tuple(map(to_aida_obj, items))
        if seed is not None:
            random.seed(seed)

    def __hash__(self) -> int:
        return hash((self.__class__.__name__, self.items))

    def render(self, ctx: Ctx) -> AidaObj:
        ret = random.choice(self.items)
        return cast(AidaObj, _update_ctx(ctx, self, ret))


class Alt(AidaObj):
    def __init__(self, main: ValidType, alt: ValidType = None) -> None:
        self.main = to_aida_obj(main)
        self.alt = to_aida_obj(alt or Empty)

    def __hash__(self) -> int:
        return hash((self.__class__.__name__, self.main, self.alt))

    def render(self, ctx: Ctx) -> AidaObj:
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
