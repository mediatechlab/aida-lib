from itertools import product
from aida import render, LangConfig, Lang, NP, GNumber, Gender, VP, GPerson

# words
subj = (NP('I')
        .push(Lang.ENGLISH, GNumber.SINGULAR)
        .add_mapping('I', GPerson.FIRST)
        .add_mapping('he', GPerson.SECOND, Gender.MALE)
        .pop().push(GNumber.PLURAL)
        .add_mapping('we', GPerson.FIRST)
        .add_mapping('they', GPerson.SECOND)
        .clear().push(Lang.PORTUGUESE, GNumber.SINGULAR)
        .add_mapping('eu', GPerson.FIRST)
        .add_mapping('ele', GPerson.SECOND, Gender.MALE)
        .pop().push(GNumber.PLURAL)
        .add_mapping('nós', GPerson.FIRST)
        .add_mapping('eles', GPerson.SECOND))

verb = (VP('make')
        .push(Lang.ENGLISH, GNumber.SINGULAR)
        .add_mapping('make', GNumber.PLURAL, GPerson.FIRST)
        .add_mapping('makes', GPerson.SECOND)
        .clear().push(Lang.PORTUGUESE, GNumber.SINGULAR)
        .add_mapping('faço', GPerson.FIRST)
        .add_mapping('faz', GPerson.SECOND)
        .pop().push(GNumber.PLURAL)
        .add_mapping('fazemos', GPerson.FIRST)
        .add_mapping('fazem', GPerson.SECOND))

cake = (NP('a cake')
        .add_mapping('a cake', Lang.ENGLISH)
        .add_mapping('um bolo', Lang.PORTUGUESE))

node = (subj | verb | cake).sentence()
conf = LangConfig(node)

for lang, person, number in product((Lang.ENGLISH, Lang.PORTUGUESE), (GNumber.SINGULAR, GNumber.PLURAL), (GPerson.FIRST, GPerson.SECOND)):
    conf.lang = lang
    conf.person = person
    conf.number = number
    print(f'lang={lang.value} person={person.value} number={number.value}:')
    print('\t', render(conf))
