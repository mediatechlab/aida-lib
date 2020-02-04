import operator
from typing import Any, Union, cast

__all__ = ['Ctx', 'render', 'Const', 'Var', 'Empty']

BasicTypes = (str, int, float, bool)
PrimaryType = Union[str, int, float, bool]
ValidType = Union['AidaObj', PrimaryType]


def to_aida_obj(obj: ValidType) -> 'AidaObj':
    if isinstance(obj, AidaObj):
        return obj
    elif isinstance(obj, BasicTypes):
        return Const(obj)
    else:
        raise Exception(f'Impossible to cast {obj} to AidaObj')


def to_operand(obj: ValidType) -> 'Operand':
    if isinstance(obj, Operand):
        return obj
    elif isinstance(obj, BasicTypes):
        return Const(obj)
    else:
        raise Exception(f'Impossible to cast {obj} to Operand')


class Ctx(object):
    def __init__(self) -> None:
        self.store = set()

    def __repr__(self) -> str:
        return f'Ctx(items={len(self.store)})'

    def contains(self, aida_obj: 'AidaObj') -> bool:
        return hash(aida_obj) in self.store

    def add(self, aida_obj: 'AidaObj') -> 'Ctx':
        self.store.add(hash(aida_obj))
        return self


class AidaObj(object):
    def render(self, ctx: Ctx) -> ValidType:
        raise NotImplementedError()


def _render(aida_obj: ValidType, ctx: Ctx = None) -> Union[AidaObj, str]:
    ctx = ctx or Ctx()
    if isinstance(aida_obj, AidaObj):
        return render(aida_obj.render(ctx), ctx)
    else:
        return str(aida_obj)


def render(aida_obj: ValidType, ctx: Ctx = None) -> str:
    return cast(str, _render(aida_obj, ctx))


def _update_ctx(ctx: Ctx, *items: ValidType) -> ValidType:
    for item in items:
        if isinstance(item, AidaObj):
            ctx.add(item)
    return items[-1]


class Operand(AidaObj):
    def __init__(self, value: Any = None) -> None:
        self.value = value

    def __hash__(self) -> int:
        return hash(self.value)

    def __repr__(self) -> str:
        return f'Op[{self.value}]'

    def render(self, ctx: Ctx):
        if isinstance(self.value, Operation):
            return self.value.eval()
        elif isinstance(self.value, AidaObj):
            return self.value.render(ctx)
        else:
            return self.value

    def __and__(self, other: ValidType) -> 'Operand':
        return Operand(Operation('and_', self, to_operand(other)))

    def __gt__(self, other: ValidType) -> 'Operand':
        return Operand(Operation('gt', self, to_operand(other)))

    def __ge__(self, other: ValidType) -> 'Operand':
        return Operand(Operation('ge', self, to_operand(other)))

    def __lt__(self, other: ValidType) -> 'Operand':
        return Operand(Operation('lt', self, to_operand(other)))

    def __le__(self, other: ValidType) -> 'Operand':
        return Operand(Operation('le', self, to_operand(other)))

    def __eq__(self, other: ValidType) -> 'Operand':
        return Operand(Operation('eq', self, to_operand(other)))

    def __ne__(self, other: ValidType) -> 'Operand':
        return Operand(Operation('ne', self, to_operand(other)))

    def __invert__(self) -> 'Operand':
        return Operand(Operation('not', self))

    def __add__(self, other: ValidType) -> 'Operand':
        return Operand(Operation('add', self, to_operand(other)))

    def __or__(self, other: ValidType) -> 'Operand':
        return Operand(Operation('or', self, to_operand(other)))

    def in_ctx(self, ctx: Ctx) -> 'Operand':
        return Operand(Operation('in_ctx', self, Operand(ctx)))


class Operation(object):
    def __init__(self, op: str, *operands: Operand) -> None:
        self.op = op
        self.operands = operands

    def __hash__(self) -> int:
        return hash((self.op, self.operands))

    def __repr__(self) -> str:
        return (f'{self.op} {self.operands[0]}' if len(self.operands) == 1
                else f'{self.operands[0]} {self.op} {self.operands[1]}')

    @staticmethod
    def _unwrap(op: Any) -> ValidType:
        if isinstance(op, Operation):
            return Operation._unwrap(op.eval())
        elif isinstance(op, Operand):
            return Operation._unwrap(op.value)
        else:
            return op

    def eval(self) -> ValidType:
        required_operands = 2 if self.op in (
            'gt', 'ge', 'lt', 'le', 'eq', 'ne', 'and_', 'in_ctx', 'add', 'or') else 1
        assert len(self.operands) == required_operands

        if self.op == 'in_ctx':
            return cast(Ctx, self.operands[1].value).contains(self.operands[0])
        elif self.op == 'not':
            return not self._unwrap(self.operands[0])
        elif self.op == 'or':
            values = list(map(Operation._unwrap, self.operands))
            if isinstance(values[0], bool) and isinstance(values[1], bool):
                return values[0] or values[1]
            else:
                return values[0] + ' ' + values[1]
        else:
            values = map(Operation._unwrap, self.operands)
            return getattr(operator, self.op)(*values)


class Const(Operand):
    def __init__(self, value: PrimaryType) -> None:
        super().__init__(value)

    def __hash__(self) -> int:
        return hash(self.value)

    def __repr__(self) -> str:
        return f'Const({self.value})'

    def render(self, ctx: Ctx) -> str:
        return cast(str, _update_ctx(ctx, self, str(self.value)))


Empty = Const('')


class Var(Operand):
    def __init__(self, name: str = None) -> None:
        super().__init__()
        self.name = name

    def __hash__(self) -> int:
        return hash((self.__class__.__name__, self.name))

    def __repr__(self) -> str:
        return f'Var({self.name}={self.value})'

    def assign(self, value: PrimaryType) -> 'Var':
        self.value = value
        return self

    def render(self, ctx: Ctx) -> str:
        assert self.value is not None
        return cast(str, _update_ctx(ctx, self, str(self.value)))
