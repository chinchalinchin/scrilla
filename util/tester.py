import requests

import util.helper as helper

def test_av_key(key):
    test_url = ""

    prices = requests.get().json()
        
    first_element = helper.get_first_json_key(prices)

    # check for bad response
    if first_element == 'Error Message':
        return False
    else:
        return True

def test_q_key(key):
    test_url = ""

    prices = requests.get().json()
        
    first_element = helper.get_first_json_key(prices)

    # check for bad response
    if first_element == 'Error Message':
        return False
    else:
        return True