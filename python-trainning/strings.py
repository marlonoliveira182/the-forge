name = input('Insert your name: ')
age = input ('your age is: ')

if name and age:
    print(f'Your name is {name}.')
    print(f'Your name written backwards is {name[::-1]}.')
    if ' ' in name:
        print(f'Your name contains spaces.')
    else:
        print(f'Your name does not contain spaces.')
    print(f'Your name contains {len(name)} letters.')
    print(f'The first letter of your name is {name[0]}.')
    print(f'The last letter of your name is {name[-1]}')
else:
    print('You did not provide your name or age.')