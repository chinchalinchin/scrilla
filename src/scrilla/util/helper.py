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
    for arg in formatter.DATE_ARG_DICT:
        parser.add_argument(formatter.DATE_ARG_DICT[arg][0], 
                            formatter.DATE_ARG_DICT[arg][1], 
                            formatter.DATE_ARG_DICT[arg][2], 
                            formatter.DATE_ARG_DICT[arg][3],
                            default=None, 
                            type=lambda s: datetime.datetime.strptime(s, '%Y-%m-%d'),
                            dest=arg)
    for arg in formatter.FLOAT_ARG_DICT:
        parser.add_argument(formatter.FLOAT_ARG_DICT[arg][0],
                            formatter.FLOAT_ARG_DICT[arg][1],
                            formatter.FLOAT_ARG_DICT[arg][2],
                            formatter.FLOAT_ARG_DICT[arg][3],
                            default=None,
                            type=float,
                            dest=arg)
    for arg in formatter.INT_ARG_DICT:
        parser.add_argument(formatter.INT_ARG_DICT[arg][0],
                            formatter.INT_ARG_DICT[arg][1],
                            formatter.INT_ARG_DICT[arg][2],
                            formatter.INT_ARG_DICT[arg][3],
                            default=None,
                            type=int,
                            dest=arg)
    for arg in formatter.STRING_ARG_DICT:
        parser.add_argument(formatter.STRING_ARG_DICT[arg][0],
                            formatter.STRING_ARG_DICT[arg][1],
                            formatter.STRING_ARG_DICT[arg][2],
                            formatter.STRING_ARG_DICT[arg][3],
                            default=None,
                            type=str,
                            dest=arg)
    for arg in formatter.BOOLEAN_ARG_DICT:
        parser.add_argument(formatter.BOOLEAN_ARG_DICT[arg][0],
                            formatter.BOOLEAN_ARG_DICT[arg][1],
                            formatter.BOOLEAN_ARG_DICT[arg][2],
                            formatter.BOOLEAN_ARG_DICT[arg][3],
                            action='store_true',
                            dest=arg)

    group = parser.add_mutually_exclusive_group()
    keys = static.keys['ESTIMATION']
    for method in keys:
        group.add_argument(formatter.ESTIMATION_ARG_DICT[keys[method]][0],
                            formatter.ESTIMATION_ARG_DICT[keys[method]][1],
                            formatter.ESTIMATION_ARG_DICT[keys[method]][2],
                            formatter.ESTIMATION_ARG_DICT[keys[method]][3],
                            action='store_const',
                            dest='estimation_method',
                            const=keys[method])

    parser.add_argument('tickers', nargs='*', type=str)
    return vars(parser.parse_args(args))

def get_first_json_key(this_json: dict) -> str:
    return list(this_json.keys())[0]

def replace_troublesome_chars(msg: str) -> str:
    return msg.replace('\u2265','').replace('\u0142', '')
