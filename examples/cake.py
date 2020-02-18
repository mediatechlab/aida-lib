from itertools import product
from aida import render, LangConfig, Lang, NP, GNumber, Gender, VP, GPerson

# words
subj = (NP('I')
        .push(Lang.ENGLISH, GNumber.SINGULAR)
        .add_mapping('I', GPerson.FIRST)
        .add_mapping('he', GPerson.THIRD)
        .pop().push(GNumber.PLURAL)
        .add_mapping('we', GPerson.FIRST)
        .add_mapping('they', GPerson.THIRD)
        .clear().push(Lang.PORTUGUESE, GNumber.SINGULAR)
        .add_mapping('eu', GPerson.FIRST)
        .add_mapping('ele', GPerson.THIRD)
        .pop().push(GNumber.PLURAL)
        .add_mapping('nós', GPerson.FIRST)
        .add_mapping('eles', GPerson.THIRD))

verb = (VP('make')
        .push(Lang.ENGLISH)
        .add_mapping('make', GNumber.SINGULAR, GNumber.PLURAL, GPerson.FIRST)
        .add_mapping('makes', GNumber.SINGULAR, GPerson.THIRD)
        .clear().push(Lang.PORTUGUESE, GNumber.SINGULAR)
        .add_mapping('faço', GPerson.FIRST)
        .add_mapping('faz', GPerson.THIRD)
        .pop().push(GNumber.PLURAL)
        .add_mapping('fazemos', GPerson.FIRST)
        .add_mapping('fazem', GPerson.THIRD))

cake = (NP('a cake')
        .add_mapping('a cake', Lang.ENGLISH)
        .add_mapping('um bolo', Lang.PORTUGUESE))

node = (subj | verb | cake).sentence()
conf = LangConfig(node)

for lang, person, number in product((Lang.ENGLISH, Lang.PORTUGUESE), (GNumber.SINGULAR, GNumber.PLURAL), (GPerson.FIRST, GPerson.THIRD)):
    conf.lang = lang
    conf.person = person
    conf.number = number
    print(f'lang={lang.value} person={person.value} number={number.value}:')
    print('\t', render(conf))
