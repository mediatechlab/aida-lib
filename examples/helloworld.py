from aida import render, Empty, Var

# create a variable to hold a name
name_var = Var('name')

# create a simple phrase
node = (Empty + 'hello,' | name_var).sentence()

# assign a value to the variable
name_var.assign('World')

# render the node
print(render(node))
