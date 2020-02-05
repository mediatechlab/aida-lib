from enum import Enum
from typing import cast

from .core import Node, Ctx, ValidType, Const


class Gender(Enum):
    NEUTRAL = 'N'
    MALE = 'M'
    FEMALE = 'F'


class Tense(Enum):
    SIMPLE_PRESENT = 'simple-present'


class Lang(Enum):
    EN_US = 'en-US'
    PT = 'pt'


class GNumber(Enum):
    SINGULAR = 'singular'
    PLURAL = 'plural'


class NP(Const):
    def __init__(self, value: str, gender=None, number=None) -> None:
        super().__init__(value)
        self.gender = gender or Gender.NEUTRAL
        self.number = number or GNumber.SINGULAR


class VP(Const):
    def __init__(self, value: str) -> None:
        super().__init__(value)


class Sentence(Const):
    def __init__(self, subj: NP, verb: VP, obj: NP, lang: Lang = None, tense: Tense = None) -> None:
        super().__init__('')
        self.subj = subj
        self.verb = verb
        self.obj = obj
        self.lang = lang or Lang.EN_US
        self.tense = tense or Tense.SIMPLE_PRESENT

    def render(self, ctx: Ctx) -> ValidType:
        # maria compra uma maçã
        # maria e júlia compram uma maçã
        # maria e júlia compram maçãs
        return (self.subj | self.verb | self.obj).sentence().render(ctx)
