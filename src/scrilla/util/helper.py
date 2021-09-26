from math import trunc

from scrilla import static
from scrilla.util import dater, formatter

################################################
##### FORMATTING FUNCTIONS
def truncate(number, digits) -> float:
    stepper = 10.0 ** digits
    return trunc(stepper * number) / stepper

def get_number_input(msg_prompt) -> str:
    while True:
        user_input = input(msg_prompt)
        if user_input.isnumeric():
            return user_input
        print('Input Not Understood. Please Enter A Numerical Value.')
    
def strip_string_array(array) -> list:
    new_array = []
    for string in array:
        new_array.append(string.strip())
    return new_array

def round_array(array, decimals):
    cutoff = (1/10**decimals)
    return [0 if element < cutoff else truncate(element, decimals) for element in array]

def intersect_dict_keys(dict1, dict2):
    intersection = [x for x in dict1.keys() if x in dict2.keys()]

    new_dict1, new_dict2 = {}, {}
    for key, value in dict1.items():
        if key in intersection:
            new_dict1[key] = value
    for key, value in dict2.items():
        if key in intersection:
            new_dict2[key] = value
    
    return new_dict1, new_dict2

################################################
##### PARSING FUNCTIONS

### CLI PARSING
def get_float_arg(xtra_args, xtra_values, which_arg):
    if which_arg in xtra_args:
        try:
            return float(xtra_values[xtra_args.index(which_arg)])
        except ValueError as ve:
            raise ve
    return None

def get_int_arg(xtra_args, xtra_values, which_arg):
    if which_arg in xtra_args:
        try:
            return int(xtra_values[xtra_args.index(which_arg)])
        except ValueError as ve:
            raise ve
    return None

def get_date_arg(xtra_args, xtra_values, which_arg):
    if which_arg in xtra_args:
        unparsed_date = xtra_values[xtra_args.index(which_arg)]
        return dater.parse_date_string(unparsed_date)
    return None

def get_str_arg(xtra_args, xtra_values, which_arg, lowerCase = False):
    if which_arg in xtra_args:
        if not lowerCase:
            return str(xtra_values[xtra_args.index(which_arg)])
        return str(xtra_values[xtra_args.index(which_arg)]).lower()
    return None

def get_flag_arg(xtra_args, which_arg):
    if which_arg in xtra_args:
        return which_arg
    return None

def format_xtra_args_dict(xtra_args, xtra_values, default_estimation_method):
    current_estimation_method = default_estimation_method
    if get_flag_arg(xtra_args, formatter.FUNC_XTRA_SINGLE_ARGS_DICT['moments']) is not None:
        current_estimation_method = static.keys['ESTIMATION']['MOMENT']
    elif get_flag_arg(xtra_args, formatter.FUNC_XTRA_SINGLE_ARGS_DICT['likelihood']) is not None:
       current_estimation_method = static.keys['ESTIMATION']['LIKE']
    elif get_flag_arg(xtra_args,formatter.FUNC_XTRA_SINGLE_ARGS_DICT['percentiles']) is not None:
       current_estimation_method = static.keys['ESTIMATION']['PERCENT']

    return {
        'start_date': get_date_arg(xtra_args, xtra_values, formatter.FUNC_XTRA_VALUED_ARGS_DICT['start_date']),
        'end_date': get_date_arg(xtra_args, xtra_values, formatter.FUNC_XTRA_VALUED_ARGS_DICT['end_date']),
        'save_file': get_str_arg(xtra_args, xtra_values, formatter.FUNC_XTRA_VALUED_ARGS_DICT['save']),
        'target': get_float_arg(xtra_args, xtra_values, formatter.FUNC_XTRA_VALUED_ARGS_DICT['target']),
        'discount': get_float_arg(xtra_args, xtra_values, formatter.FUNC_XTRA_VALUED_ARGS_DICT['discount']),
        'investment': get_float_arg(xtra_args, xtra_values, formatter.FUNC_XTRA_VALUED_ARGS_DICT['investment']),
        'expiry': get_float_arg(xtra_args, xtra_values, formatter.FUNC_XTRA_VALUED_ARGS_DICT['expiry']),
        'probability': get_float_arg(xtra_args, xtra_values, formatter.FUNC_XTRA_VALUED_ARGS_DICT['probability']),
        'model': get_str_arg(xtra_args, xtra_values,formatter.FUNC_XTRA_VALUED_ARGS_DICT['model'], True),
        'steps': get_int_arg(xtra_args, xtra_values,formatter.FUNC_XTRA_VALUED_ARGS_DICT['steps']),
        'optimize_sharpe': get_flag_arg(xtra_args, formatter.FUNC_XTRA_SINGLE_ARGS_DICT['optimize_sharpe']),
        'suppress': get_flag_arg(xtra_args,formatter.FUNC_XTRA_SINGLE_ARGS_DICT['suppress_output']),
        'json': get_flag_arg(xtra_args, formatter.FUNC_XTRA_SINGLE_ARGS_DICT['json']),
        'estimation': current_estimation_method
    }

def separate_and_parse_args(args):
    extra_args, extra_values= [], []
    reduced_args = args
    
    for arg in args:
        if arg in formatter.FUNC_XTRA_VALUED_ARGS_DICT.values() or arg in formatter.FUNC_XTRA_SINGLE_ARGS_DICT.values():
            extra_args.append(arg)
            if arg not in formatter.FUNC_XTRA_SINGLE_ARGS_DICT.values():
                extra_values.append(args[args.index(arg)+1])
            else:
                extra_values.append(None)

    for arg in extra_args:
        reduced_args.remove(arg)

    for arg in extra_values:
        if arg is not None:
            reduced_args.remove(arg)

    extra_reduced_args = reduced_args
    offset = 0
    for i, arg in enumerate(reduced_args):
        if arg.startswith('-'):
            extra_reduced_args.remove(arg)
            offset += 1
        else:
            extra_reduced_args[i-offset] = extra_reduced_args[i-offset].upper()

    return (extra_args, extra_values, extra_reduced_args)
    
def get_first_json_key(this_json):
    return list(this_json.keys())[0]

def replace_troublesome_chars(msg):
    return msg.replace('\u2265','').replace('\u0142', '')
