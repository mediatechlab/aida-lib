from typing import cast

import aida
from aida.core import Operation


def test_render_simple_choice():
    x = aida.Var()
    x.assign('Alice')
    y = aida.Var()
    y.assign('Bob')
    choices = aida.Choices(x, y, seed=42)

    assert aida.render(choices) == 'Alice'

    x.assign('Chris')
    assert aida.render(choices) == 'Chris'


def test_concat():
    x = aida.Var('name')
    x.assign('Alice')
    sent = aida.Const('good')
    ctx = aida.Ctx()

    node = x | 'is a' | sent | 'person.'
    assert aida.render(node, ctx) == 'Alice is a good person.'

    x.assign('Bob')
    assert aida.render(node, ctx) == 'Bob is a good person.'


def test_alt():
    x = aida.Const('Alice')
    other_names = aida.Choices('Bob', 'Chris', seed=42)
    ctx = aida.Ctx()
    alt = aida.create_alt(x, other_names)

    assert aida.render(alt, ctx) == 'Alice'
    assert aida.render(alt, ctx) == 'Bob'


def test_enumerate():
    assert aida.render(aida.Enumeration('Alice')) == 'Alice'
    assert aida.render(aida.Enumeration('Alice', 'Bob')) == 'Alice and Bob'
    assert aida.render(aida.Enumeration(
        'Alice', 'Bob', 'Chris')) == 'Alice, Bob, and Chris'


def test_branch():
    x = aida.Var('val')
    k = aida.Const(3)
    t = aida.Const(True)
    branch = aida.Branch((x > k) & (t == True), 'greater', 'not greater')

    x.assign(1)
    assert aida.render(branch) == 'not greater'

    x.assign(5)
    assert aida.render(branch) == 'greater'

    branch = aida.Branch((x > k) & (t == False), 'greater', 'not greater')
    assert aida.render(branch) == 'not greater'


def test_arithmetic():
    ctx = aida.Ctx()
    x = aida.Var('x')
    cond = (x + 1) > 2

    x.assign(2)
    assert cast(Operation, cond.value).render(ctx)

    x.assign(1)
    assert not cast(Operation, cond.value).render(ctx)


def test_in_ctx():
    ctx = aida.Ctx()
    k = aida.Const('Alice')
    branch = aida.Branch(k.in_ctx(), 'yes', 'no')

    assert aida.render(branch, ctx=ctx) == 'no'

    k.render(ctx)
    assert aida.render(branch, ctx=ctx) == 'yes'


def test_sentence_ctx():
    ref = aida.create_ref('Geralt of Rivia', 'Geralt')
    sentence = aida.Empty + 'Toss a coin to' | ref + '.'

    ctx = aida.Ctx()
    assert aida.render(sentence, ctx=ctx) == 'Toss a coin to Geralt of Rivia.'
    assert aida.render(sentence, ctx=ctx) == 'Toss a coin to Geralt.'
    assert aida.render(sentence, ctx=ctx) == 'Toss a coin to Geralt.'

    sentence2 = ref | 'is nice.'
    assert aida.render(sentence2, ctx=ctx) == 'Geralt is nice.'


def test_phrase():
    phrase = (aida.Empty + 'this is a phrase').to_phrase()
    assert aida.render(phrase) == 'This is a phrase.'


def test_injector():
    a = aida.Var('a')
    b = aida.Var('b')

    node = a | b
    inj = aida.Injector([a, b], node)

    inj.assign([{'a': 'a1', 'b': 'b1'}, {'a': 'a2', 'b': 'b2'}])
    assert aida.render(inj) == 'a1 b1'
    assert aida.render(inj) == 'a2 b2'
