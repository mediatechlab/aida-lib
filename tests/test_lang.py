import aida


def test_enumerate():
    # english
    conf = aida.LangConfig(aida.Empty)
    assert aida.render(aida.create_enumeration(conf, 'Alice')) == 'Alice'
    assert aida.render(aida.create_enumeration(
        conf, 'Alice', 'Bob')) == 'Alice and Bob'
    assert aida.render(aida.create_enumeration(
        conf, 'Alice', 'Bob', 'Chris')) == 'Alice, Bob, and Chris'

    # portuguese
    conf.lang = aida.Lang.PORTUGUESE
    assert aida.render(aida.create_enumeration(conf, 'Alice')) == 'Alice'
    assert aida.render(aida.create_enumeration(
        conf, 'Alice', 'Bob')) == 'Alice e Bob'
    assert aida.render(aida.create_enumeration(
        conf, 'Alice', 'Bob', 'Chris')) == 'Alice, Bob e Chris'
