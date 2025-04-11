first_value = input ('Please insert your first value:')
second_value = input ('Please insert your second value:')
first_value = float (first_value)
second_value = float (second_value)

print(first_value, second_value)

if first_value > second_value:
    print(f'First value ({first_value:.2f}) is greater than second value ({second_value:.2f})')
elif first_value < second_value:
    print(f'Second value ({second_value:.2f}) is greater than first value ({first_value:.2f})')
else:
    print ('Values are the same!')