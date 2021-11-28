import pytest
from httmock import HTTMock

from scrilla import settings as scrilla_settings
from scrilla.util import dater
from scrilla.analysis.models.geometric import statistics
from scrilla.cache import PriceCache, ProfileCache, InterestCache, CorrelationCache
from scrilla.files import clear_directory

from .. import mock

@pytest.fixture(autouse=True)
def reset_cache():
    clear_directory(scrilla_settings.CACHE_DIR)
    PriceCache(), ProfileCache(), InterestCache(), CorrelationCache()
    return

@pytest.mark.parametrize("ticker,start_date,end_date", [
    ('ALLY', '2021-11-12', '2021-11-12'),
    ('BX', '2021-10-29', '2021-11-05'),
    ('ALLY', '2021-08-04','2021-09-10')
])
def test_moving_average_return(ticker, start_date, end_date):
    with HTTMock(mock.mock_prices):
        moving_average = statistics.calculate_moving_averages(ticker=ticker, start_date=start_date, end_date=end_date)

    assert(isinstance(moving_average, dict))
    assert(len(list(moving_average.keys())) == dater.business_days_between(start_date, end_date))
    assert(start_date in list(moving_average.keys()))
    assert(all(isinstance(averages,dict) for averages in moving_average.values()))
    assert(all([all([isinstance(average,float) for average in average_dict.values()]) for average_dict in moving_average.values()]))
