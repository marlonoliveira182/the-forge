name = input ('Insert your name: ').lower()
letter = input ('Insert the letter to be looked for: ').lower()
# letter = letter.lower()
# name = name.lower()
print(name)
if letter not in name:
    print (f'Name {name} does not have the letter "{letter}"')
else:
    print (f'Name {name} has the letter "{letter}"')