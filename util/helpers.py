# Application Helper Functions

def get_number_input(msg_prompt):
    flag = False 
    while flag is not True:
        user_input = input(msg_prompt)
        if isinstance(float(user_input), float):
            return user_input
        else:
            print('Input Not Understood. Please Enter A Numerical Value.')
