import aida


def test_render_simple_choice():
    x = aida.Var()
    x.assign('Alice')
    y = aida.Var()
    y.assign('Bob')
    choices = aida.Choices([x, y], seed=42)

    assert aida.render(choices) == 'Alice'

    x.assign('Chris')
    assert aida.render(choices) == 'Chris'


def test_concat():
    x = aida.Var('name')
    x.assign('Alice')
    sent = aida.Const('good')
    ctx = aida.Ctx()

    node = x | 'is a' | sent | 'person.'
    assert node.render(ctx) == 'Alice is a good person.'

    x.assign('Bob')
    assert node.render(ctx) == 'Bob is a good person.'


def test_alt():
    x = aida.Var('name')
    x.assign('Alice')

    other_names = aida.Choices(['Bob', 'Chris'], seed=42)
    ctx = aida.Ctx()
    alt = aida.Alt(x, other_names)

    assert aida.render(alt, ctx) == 'Alice'
    assert aida.render(alt, ctx) == 'Bob'


def test_enumerate():
    assert aida.render(aida.Enumeration(['Alice'])) == 'Alice'
    assert aida.render(aida.Enumeration(['Alice', 'Bob'])) == 'Alice and Bob'
    assert aida.render(aida.Enumeration(
        ['Alice', 'Bob', 'Chris'])) == 'Alice, Bob, and Chris'


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
