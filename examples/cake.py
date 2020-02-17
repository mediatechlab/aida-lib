from itertools import product
from aida import render, LangConfig, Lang, NP, GNumber, Gender, VP, GPerson

# words
subj = (NP('I')
        .add_mapping('I', GNumber.SINGULAR, GPerson.FIRST, Lang.ENGLISH)
        .add_mapping('he', GNumber.SINGULAR, GPerson.SECOND, Gender.MALE, Lang.ENGLISH)
        .add_mapping('they', GNumber.PLURAL, GPerson.SECOND, Lang.ENGLISH)
        .add_mapping('we', GNumber.PLURAL, GPerson.FIRST, Lang.ENGLISH)
        .add_mapping('eu', GNumber.SINGULAR, GPerson.FIRST, Lang.PORTUGUESE)
        .add_mapping('ele', GNumber.SINGULAR, GPerson.SECOND, Lang.PORTUGUESE)
        .add_mapping('nós', GNumber.PLURAL, GPerson.FIRST, Lang.PORTUGUESE)
        .add_mapping('eles', GNumber.PLURAL, GPerson.SECOND, Lang.PORTUGUESE))

verb = (VP('make')
        .add_mapping('make', GNumber.SINGULAR, GNumber.PLURAL, GPerson.FIRST, Lang.ENGLISH)
        .add_mapping('makes', GNumber.SINGULAR, GPerson.SECOND, Lang.ENGLISH)
        .add_mapping('faz', GNumber.SINGULAR, GPerson.SECOND, Lang.PORTUGUESE)
        .add_mapping('faço', GNumber.SINGULAR, GPerson.FIRST, Lang.PORTUGUESE)
        .add_mapping('fazemos', GNumber.PLURAL, GPerson.FIRST, Lang.PORTUGUESE)
        .add_mapping('fazem', GNumber.PLURAL, GPerson.SECOND, Lang.PORTUGUESE))

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
