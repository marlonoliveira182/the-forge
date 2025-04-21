phrase = 'O Python é uma linguagem de programação multiparadigma. Python foi criado por Guido van Rossum.'.lower().strip()
highest_count = 0
letter_highest_count = ''


i = 0
#Phrase iteration
while i < len(phrase):
    current_letter = phrase[i]
    current_letter_count = phrase.count(current_letter) #Returns the count of current letter
    #print(current_letter, current_letter_count)
    if current_letter != ' ' and current_letter_count > highest_count: #Check if current letter is not a space and appears most often
        highest_count = current_letter_count
        letter_highest_count = current_letter

    i += 1

# Find all letters with the highest count
letters_with_highest_count = [letter for letter in set(phrase) if letter != ' ' and phrase.count(letter) == highest_count]

if len(letters_with_highest_count) > 1:
    print(
        f'There is a tie! The letters with the most appearances are {", ".join(letters_with_highest_count)}, each appearing {highest_count} times.')
else:
    print(
        f'The letter with the most appearances in the phrase is "{letter_highest_count}", appearing {highest_count} times.')
