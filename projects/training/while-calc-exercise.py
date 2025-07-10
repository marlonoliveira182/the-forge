# Flag that validates if user wants to exit or not
exit_flag = False
# Flag that validates if calc process returned errors
errors_found = False

while not exit_flag:
    errors_found = None
    while not errors_found:
        first_number = input('Insert the first number:\n')
        second_number = input('Insert the second number:\n')

        # Converts input numbers from strings to float
        try:
            first_number = float(first_number)
            second_number = float(second_number)
        except ValueError:
            print('You did not enter valid numbers.')
            errors_found = True
            continue

        operation = input('Insert the operation (+-*/):\n').strip()

        # Validates supported operations and execute it if user entered a valid one
        if operation == '+':
            result = first_number + second_number
            print(f'The result of the operation is:\n {result:.2f}')
            break
        elif operation == '-':
            result = first_number - second_number
            print(f'The result of the operation is:\n {result:.2f}')
            break
        elif operation == '*':
            result = first_number * second_number
            print(f'The result of the operation is:\n {result:.2f}')
            break
        elif operation == '/':
            if second_number == 0:
                print('Error: Division by zero is not allowed.')
                errors_found = True
                print()
                break
            else:
                result = first_number / second_number
                print(f'The result of the operation is:\n {result:.2f}')
                break
        else:
            print('Unsupported operation.')
            errors_found = True
            print()
            break

    exit_flag = input('Do you want to exit?\n[Y]es/[N]o: ').strip().lower().startswith('y')
   