name = 'Marlon'
last_name = 'Oliveira'
age = 28
height = 1.72
birthday = '1996-11-24'
birth_year = int(birthday.split('-')[0])  # Extraindo o ano de nascimento
is_adult = age >= 18

# Exibindo os dados do usuário
print("Nome:", name)
print("Sobrenome:", last_name)
print("Idade:", age)
print("Altura:", height)
print("Ano de Nascimento:", birth_year)
print("É maior de idade?", is_adult)
