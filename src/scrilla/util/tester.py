import requests

import  util.helper as helper

def test_av_key(key):
    test_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=GOOG&apikey={key}'

    prices = requests.get(test_url).json()
        
    first_element = helper.get_first_json_key(prices)

    # check for bad response
    if first_element == 'Error Message':
        return False
    
    return True

def test_q_key(key):
    test_url = f'https://www.quandl.com/api/v3/datasets/FRED/NROUST?api_key={key}'

    status = requests.get(test_url).status_code
    
    # check for bad response
    if status == 400:
        return False
    
    return True