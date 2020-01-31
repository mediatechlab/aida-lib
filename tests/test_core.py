import aida.core as aida


def test_render_simple_choice():
    x = aida.Slot()
    x.assign('Alice')
    y = aida.Slot()
    y.assign('Bob')
    choices = aida.Choices([x, y], seed=42)

    assert aida.render(choices) == 'Alice'

    x.assign('Chris')
    assert aida.render(choices) == 'Chris'


def test_concat():
    x = aida.Slot('name')
    x.assign('Alice')
    sent = aida.Const('good')
    ctx = aida.Ctx()

    node = x + 'is a' + sent + 'person.'
    assert node.render(ctx) == 'Alice is a good person.'

    x.assign('Bob')
    assert node.render(ctx) == 'Bob is a good person.'


def test_alt():
    x = aida.Slot('name')
    x.assign('Alice')

    other_names = aida.Choices(['Bob', 'Chris'], seed=42)
    ctx = aida.Ctx()
    alt = aida.Alt(x, other_names)

    assert alt.render(ctx) == 'Alice'
    assert alt.render(ctx) == 'Bob'
