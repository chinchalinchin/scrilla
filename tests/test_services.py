import pytest 
import os
import requests
from httmock import urlmatch, HTTMock

from scrilla import services
from scrilla.files import load_file

from . import settings

ally_response = load_file(os.path.join(settings.MOCK_DIR, 'ally_response.json'))

@urlmatch(netloc=r'(.*\.)?alphavantage\.co*$')
def mock_prices(url, request):
    return 'Feeling lucky, punk?'

def test_service_call():
    with HTTMock(mock_prices):
        response = requests.get('https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&outputsize=full&symbol=ALLY&apikey=*')
    assert(response.text == 'Feeling lucky, punk?')
