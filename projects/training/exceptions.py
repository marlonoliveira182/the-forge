'''
My Code
'''

user_age = input('Please insert your age: ')
try:
    int(user_age)
    birth_year = 2025 - user_age
    print(f'You were born in {birth_year}')
except:
    print(f'You typed "{user_age}", which is not a number.')


'''
Trainning Code
'''


"""
Introdução ao try/except
try -> tentar executar o código
except -> ocorreu algum erro ao tentar executar
"""
numero_str = input(
    'Vou dobrar o número que vc digitar: '
)

try:
    numero_float = float(numero_str)
    print('FLOAT:', numero_float)
    print(f'O dobro de {numero_str} é {numero_float * 2:.2f}')
except:
    print('Isso não é um número')

# if numero_str.isdigit():
#     numero_float = float(numero_str)
#     print(f'O dobro de {numero_str} é {numero_float * 2:.2f}')
# else:
#     print('Isso não é um número')