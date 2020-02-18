# Aida Lib

![](https://github.com/mediatechlab/aida-lib/workflows/Python%20package/badge.svg)

Aida is a language agnostic library for text generation.

## Usage

A simple hello world script would look like this:

```Python
from aida import render, Empty, Var

# create a variable to hold a name
name_var = Var('name')

# create a simple phrase
node = (Empty + 'hello,' | name_var).to_phrase()

# assign a value to the variable
name_var.assign('World')

# render the node
print(render(node))  # 'Hello, World.'
```

## Install

Download and install with pip:

```bash
pip install aidalib
```

## Core Concepts

When using Aida, first you compose a tree of operations on your text that include conditions via branches and other control flow. Later, you fill the tree with data and render the text.

A building block is the variable class: `Var`. Use it to represent a value that you want to control later. A variable can hold numbers (e.g. `float`, `int`) or strings.

You can create branches and complex logic with `Branch`. In the example below, if `x` is greater than 1, it will render `many`, otherwise `single`.

```Python
x = Var('x')
Branch(x > 1, 'many', 'single')
```

### Context

The context, represented by the class `Ctx`, is useful to create rules that depends on what has been written before. Each object or literal that is passed to Aida is remembered by the context.

```Python
name = Const('Bob')
alt_name = Const('He')
bob = Branch(~name.in_ctx(), name, alt_name)
ctx = Ctx()

render(bob | 'is a cool guy.' | bob | 'doesn\'t mind.', ctx)
# Bob is a cool guy. He doesn't mind.
```

Creating a reference expression is a common use-case, so we have a helper function called `create_ref`.

```Python
bob = create_ref('Bob', 'He')
```

### Operators

You can compose operations on your text with some handy operators.

#### Concatenation (`+` and `|`)

```Python
'the' | 'quick' | 'brown' | 'fox'  # 'the quick brown fox'

'the' + 'quick' + 'brown' + 'fox'  # 'thequickbrownfox'
```

#### Check context (`in_ctx`)

Check if the current node is in the context.

```Python
Const('something').in_ctx()
```

#### Create a sentence (`sentence`)

Formats a line into a sentence, capitalizing the first word and adding a period.

```Python
Const('hello world').sentence()  # 'Hello world.'
```

#### Logical and numeric operators

| operator              | example  |
| --------------------- | -------- |
| negation              | `!x`     |
| greater than          | `x > y`  |
| greater or equal than | `x >= y` |
| less than             | `x < y`  |
| less or equal than    | `x <= y` |
| equal                 | `x == y` |
| not equal             | `x != y` |
| or                    | `x | y`  |
| and                   | `x & y`  |
| plus                  | `x + y`  |

### Random choice

Randomly draws one node from a list of possibilities.

```Python
Choice('Alice', 'Bob', 'Chris')  # either 'Alice', 'Bob', or 'Chris'
```

### Injector

The `Injector` class assigns values to variables from a list each time it is rendered. Very useful to automatically fill values based on data.

```Python
animal = Var('animal')
sound = Var('sound')
node = animal | 'makes' | sound
node = Injector([animal, sound], node)

# assign multiple values
node.assign([
  {'animal': 'cat', 'sound': 'meaw'},
  {'animal': 'dog', 'sound': 'roof'},
])

render(node) # 'cat makes meaw'

render(node) # 'dog makes roof'
```

### For-loops with `Repeat`

Use `Repeat` to render a node multiple times. At the simplest level, you have this:

```Python
render(Repeat('buffalo').assign(8))
# 'buffalo buffalo buffalo buffalo buffalo buffalo buffalo buffalo'
```

`Repeat` is very useful when used with `Injector`, like this:

```Python
animal = Var('animal')
sound = Var('sound')
node = animal | 'makes' | sound
node = Injector([animal, sound], node)
repeat = Repeat(node)

# assign multiple values
data = [
  {'animal': 'cat', 'sound': 'meaw'},
  {'animal': 'dog', 'sound': 'roof'},
]
node.assign(data)
repeat.assign(len(data))

# renders text based on data
render(node)  # cat makes meaw dog makes roof
```

## Language Concepts

There are some experimental features that allows you to create text that adapts to common language features, like grammatical _number_ and _person_.

### Enumerate items

Use `LangConfig` to setup language features and then call `create_enumeration()`.

```Python
from aida import create_enumeration, LangConfig, Lang, render

render(create_enumeration(LangConfig(lang=Lang.ENGLISH), 'Alice', 'Bob', 'Chris'))
# 'Alice, Bob, and Chris'

render(create_enumeration(LangConfig(lang=Lang.PORTUGUESE), 'Alice', 'Bob', 'Chris'))
# 'Alice, Bob e Chris'
```

### Sentence Structure

You can compose sentences using special structures: `NP` (noun phrase) and `VP` (verb phrase) along with `LangConfig`.

```Python
from aida import NP, VP, LangConfig

subj = NP('the dog')
verb = VP('barked')

s = (subj | verb).sentence()

render(LangConfig(s))  # The dog barked.
```

What really makes this different from just using `Const` is that we can create rules that change the output of `NP` and `VP` based on various language features. The system will try to use the rule that matches most features from the given `LangConfig`.

```Python
from aida import NP, VP, LangConfig, GNumber, GPerson

subj = (NP('I')
        .add_mapping('I', GNumber.SINGULAR, GPerson.FIRST)
        .add_mapping('he', GNumber.SINGULAR, GPerson.THIRD))
        .add_mapping('we', GNumber.PLURAL, GPerson.FIRST))
verb = (VP('drive')
        .add_mapping('drive', GPerson.FIRST)
        .add_mapping('drives', GPerson.THIRD))

s = (subj | verb | 'a nice car').sentence()

render(LangConfig(s, number=GNumber.SINGULAR, person=GPerson.FIRST))  # I drive a nice car.
render(LangConfig(s, number=GNumber.SINGULAR, person=GPerson.THIRD))  # He drives a nice car.
render(LangConfig(s, number=GNumber.PLURAL, person=GPerson.FIRST))  # We drive a nice car.
```

## Examples

Check more complex uses at the [examples folder](examples).

## License

Licensed under the [MIT License](LICENSE).
