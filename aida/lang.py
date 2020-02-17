from enum import Enum
from typing import Dict, FrozenSet, Optional, Tuple, cast, Any

from .core import Ctx, Empty, Node, Node, ValidType, _render, to_node

__all__ = ['Gender', 'Lang', 'GNumber', 'GPerson',
           'create_enumeration', 'NP', 'VP', 'LangConfig']

LangMapping = Dict[FrozenSet, str]


class Gender(Enum):
    NEUTRAL = 'N'
    MALE = 'M'
    FEMALE = 'F'


class Lang(Enum):
    ENGLISH = 'english'
    PORTUGUESE = 'portuguese'


class GNumber(Enum):
    SINGULAR = 'singular'
    PLURAL = 'plural'


class GPerson(Enum):
    FIRST = 'first'
    SECOND = 'second'
    THIRD = 'third'


class LangElement(Node):
    def __init__(self, value: ValidType) -> None:
        super().__init__(value)
        self._parent_config_cache = None
        self.mappings: LangMapping = {}

    def __hash__(self) -> int:
        config = self.get_parent_config()
        return hash((config, self.value))

    def _render(self, ctx: Ctx, key: FrozenSet) -> ValidType:
        greatest_subset = frozenset()
        best_key = None
        for fs_key in self.mappings:
            subset = fs_key.intersection(key)
            if len(subset) > len(greatest_subset):
                greatest_subset = subset
                best_key = fs_key

        return self.mappings[best_key] if best_key else self.value

    def add_mapping(self, value: str, *key) -> 'LangElement':
        self.mappings[frozenset(key)] = value
        return self

    def get_parent_config(self):
        if not self._parent_config_cache:
            parent: Optional[Node] = self.parent
            while parent:
                if isinstance(parent, LangConfig):
                    self._parent_config_cache = parent
                    break
                else:
                    parent = cast(Node, parent).parent

        return self._parent_config_cache


class PhraseElement(LangElement):
    def __init__(self, value) -> None:
        super().__init__(value)

    def render(self, ctx: Ctx) -> ValidType:
        config = self.get_parent_config()
        assert config
        return self._render(ctx, cast(LangConfig, config).features)


class NP(PhraseElement):
    pass


class VP(PhraseElement):
    pass


class LangConfig(LangElement):
    def __init__(self, value: ValidType, lang=None, number=None, person=None, gender=None) -> None:
        super().__init__(value)
        self.lang = lang or Lang.ENGLISH
        self.number = number or GNumber.SINGULAR
        self.person = person or GPerson.FIRST
        self.gender = gender or Gender.NEUTRAL

    @property
    def features(self) -> FrozenSet:
        return frozenset((self.lang, self.number, self.person, self.gender)) - frozenset((None, ))

    def render(self, ctx: Ctx) -> ValidType:
        return _render(self.value, ctx)


def create_enumeration(config: LangConfig, *nodes: ValidType) -> Node:
    config = config or LangConfig('')
    _nodes = tuple(to_node(node) for node in nodes)

    assert config.lang in (
        Lang.ENGLISH, Lang.PORTUGUESE), 'Language not supported.'

    if len(_nodes) == 0:
        return Empty
    elif len(_nodes) == 1:
        return _nodes[0]
    elif len(_nodes) == 2:
        if config.lang == Lang.ENGLISH:
            return _nodes[0] | 'and' | _nodes[1]
        else:
            return _nodes[0] | 'e' | _nodes[1]
    else:
        comma_nodes = _nodes[1:-2]
        ret_node = _nodes[0]
        for node in comma_nodes:
            ret_node = ret_node + ',' | node

        if config.lang == Lang.ENGLISH:
            return ret_node + ', ' + _nodes[-2] + ', and ' + _nodes[-1]
        else:
            return ret_node + ', ' + _nodes[-2] + ' e ' + _nodes[-1]
