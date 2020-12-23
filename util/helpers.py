# Application Helper Functions

def get_number_input(msg_prompt):
    while True:
        user_input = input(msg_prompt)
        if user_input.isnumeric():
            return user_input
        else:
            print('Input Not Understood. Please Enter A Numerical Value.')
