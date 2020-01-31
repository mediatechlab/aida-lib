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

    node = x + 'is a' + sent + 'guy.'
    assert node.render() == 'Alice is a good guy.'

    x.assign('Bob')
    assert node.render() == 'Bob is a good guy.'
