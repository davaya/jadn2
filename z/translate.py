from base import Base, add_methods
import french
import spanish

add_methods(french)
add_methods(spanish)

b = Base()
input = 'bonjour le monde'
b.fr_setter(input)
out = b.es_getter()
print(f'In: {input}, Logical: {b.text}, Out: {out}')
