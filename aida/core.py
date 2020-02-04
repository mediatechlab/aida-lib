import operator
from typing import Union, cast

__all__ = ['Ctx', 'render', 'Const', 'Var', 'Empty']

BasicTypes = (str, int, float, bool)
PrimaryType = Union[str, int, float, bool]
ValidType = Union['Node', PrimaryType]


def to_node(obj: ValidType) -> 'Node':
    if isinstance(obj, Node):
        return obj
    elif isinstance(obj, BasicTypes):
        return Const(obj)
    else:
        raise Exception(f'Impossible to cast {obj} to Node')


class Ctx(object):
    '''
    Context is used to store items that have been rendered.
    One common application is checking if something is in context.
    '''

    def __init__(self) -> None:
        self.store = set()

    def __repr__(self) -> str:
        return f'Ctx(items={len(self.store)})'

    def contains(self, obj: 'Node') -> bool:
        return hash(obj) in self.store

    def add(self, obj: 'Node') -> 'Ctx':
        self.store.add(hash(obj))
        return self


def _render(obj: ValidType, ctx: Ctx) -> ValidType:
    if isinstance(obj, Node):
        return _render(obj.render(ctx), ctx)
    else:
        return obj


def render(obj: ValidType, ctx: Ctx = None) -> str:
    return str(_render(obj, ctx or Ctx()))


def _update_ctx(ctx: Ctx, *items: ValidType) -> ValidType:
    for item in items:
        if isinstance(item, Node):
            ctx.add(item)
    return items[-1]


class Node(object):
    '''
    Basic building block for the render tree.
    '''

    def __init__(self, value: Union[ValidType, 'Operation']) -> None:
        self.value = value

    def __hash__(self) -> int:
        return hash(self.value)

    def __repr__(self) -> str:
        return f'Node[{self.value}]'

    def render(self, ctx: Ctx) -> ValidType:
        if isinstance(self.value, Node):
            return self.value.render(ctx)
        else:
            return self.value

    def __and__(self, other: ValidType) -> 'Node':
        return Node(Operation('and_', self, to_node(other)))

    def __gt__(self, other: ValidType) -> 'Node':
        return Node(Operation('gt', self, to_node(other)))

    def __ge__(self, other: ValidType) -> 'Node':
        return Node(Operation('ge', self, to_node(other)))

    def __lt__(self, other: ValidType) -> 'Node':
        return Node(Operation('lt', self, to_node(other)))

    def __le__(self, other: ValidType) -> 'Node':
        return Node(Operation('le', self, to_node(other)))

    def __eq__(self, other: ValidType) -> 'Node':
        return Node(Operation('eq', self, to_node(other)))

    def __ne__(self, other: ValidType) -> 'Node':
        return Node(Operation('ne', self, to_node(other)))

    def __invert__(self) -> 'Node':
        return Node(Operation('not', self))

    def __add__(self, other: ValidType) -> 'Node':
        return Node(Operation('add', self, to_node(other)))

    def __or__(self, other: ValidType) -> 'Node':
        return Node(Operation('or', self, to_node(other)))

    def in_ctx(self) -> 'Node':
        return Node(Operation('in_ctx', self))


class Operation(Node):
    '''
    Special kind of node that represents an operation applied to its children.
    '''

    def __init__(self, op: str, *operands: ValidType) -> None:
        super().__init__(Empty)
        self.op = op
        self.operands = tuple(map(to_node, operands))

    def __hash__(self) -> int:
        return hash((self.op, self.operands))

    def __repr__(self) -> str:
        return (f'{self.op} {self.operands[0]}' if len(self.operands) == 1
                else f'{self.operands[0]} {self.op} {self.operands[1]}')

    def render(self, ctx: Ctx) -> ValidType:
        required_operands = 2 if self.op in (
            'gt', 'ge', 'lt', 'le', 'eq', 'ne', 'and_', 'add', 'or') else 1
        assert len(self.operands) == required_operands

        if self.op == 'in_ctx':
            return ctx.contains(self.operands[0])
        elif self.op == 'not':
            return not _render(self.operands[0], ctx)
        elif self.op == 'or':
            values = [_render(op, ctx) for op in self.operands]
            if isinstance(values[0], bool) and isinstance(values[1], bool):
                return values[0] or values[1]
            else:
                return values[0] + ' ' + values[1]
        else:
            values = (_render(op, ctx) for op in self.operands)
            return getattr(operator, self.op)(*values)


class Const(Node):
    '''
    A constant value, like 3 or 'hi'.
    '''

    def __init__(self, value: PrimaryType) -> None:
        super().__init__(value)

    def __hash__(self) -> int:
        return hash(self.value)

    def __repr__(self) -> str:
        return f'Const({self.value})'

    def render(self, ctx: Ctx) -> str:
        return cast(str, _update_ctx(ctx, self, str(self.value)))


Empty = Const('')


class Var(Node):
    '''
    A variable that can be assigned a value.
    '''

    def __init__(self, name: str = None) -> None:
        super().__init__(Empty)
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
