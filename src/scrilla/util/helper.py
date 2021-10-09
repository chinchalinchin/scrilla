import argparse, datetime
from math import trunc
from typing import Any, List, Tuple

from scrilla import static
from scrilla.util import dater, formatter

################################################
##### FORMATTING FUNCTIONS
def truncate(number, digits) -> float:
    stepper = 10.0 ** digits
    return trunc(stepper * number) / stepper

def strip_string_array(array) -> List[str]:
    new_array = []
    for string in array:
        new_array.append(string.strip())
    return new_array

def round_array(array, decimals) -> List[float]:
    cutoff = (1/10**decimals)
    return [0 if element < cutoff else truncate(element, decimals) for element in array]

def intersect_dict_keys(dict1: dict, dict2: dict) -> Tuple[dict, dict]:
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
def format_args(args) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    main_group = parser.add_mutually_exclusive_group()

    for func in formatter.FUNC_DICT:
        main_group.add_argument(formatter.FUNC_DICT[func]['values'][0],
                                formatter.FUNC_DICT[func]['values'][1],
                                action='store_const',
                                dest='function_arg',
                                const=func)

    groups = [parser.add_mutually_exclusive_group() for arg_group in formatter.ARG_DICT['META']['groups'] ]

    for arg in formatter.ARG_DICT:
        if formatter.ARG_DICT[arg]['format'] != 'group':
            parser.add_argument(formatter.ARG_DICT[arg]['values'][0], 
                                formatter.ARG_DICT[arg]['values'][1], 
                                formatter.ARG_DICT[arg]['values'][2], 
                                formatter.ARG_DICT[arg]['values'][3],
                                default=None, 
                                type=formatter.ARG_DICT[arg]['format'],
                                dest=arg)
        else:
            group_index = formatter.ARG_DICT['META']['groups'].index(formatter.ARG_DICT[arg]['group'])
            groups[group_index].add_argument(formatter.ARG_DICT[arg]['values'][0],
                                            formatter.ARG_DICT[arg]['values'][1],
                                            formatter.ARG_DICT[arg]['values'][2],
                                            formatter.ARG_DICT[arg]['values'][3],
                                            action='store_const',
                                            dest=formatter.ARG_DICT[arg]['group'],
                                            const=arg)

    parser.add_argument('tickers', nargs='*', type=str)
    return vars(parser.parse_args(args))

def get_first_json_key(this_json: dict) -> str:
    return list(this_json.keys())[0]

def replace_troublesome_chars(msg: str) -> str:
    return msg.replace('\u2265','').replace('\u0142', '')
