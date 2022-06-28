import pytest
from httmock import HTTMock

from scrilla.util.errors import SampleSizeError
from scrilla.util import dater
from scrilla.analysis.models.geometric import statistics
from scrilla.analysis.estimators import standardize
from scrilla.cache import PriceCache, ProfileCache, InterestCache, CorrelationCache
from scrilla.files import clear_cache, get_asset_type
from scrilla.static.keys import keys

from .. import mock_data


@pytest.fixture(autouse=True)
def reset_cache():
    clear_cache(mode='sqlite')
    PriceCache(mode='sqlite'), ProfileCache(mode='sqlite') 
    InterestCache(mode='sqlite'), CorrelationCache(mode='sqlite')


@pytest.mark.parametrize("ticker,start_date,end_date", mock_data.service_price_cases)
def test_moving_average_return(ticker, start_date, end_date):
    with HTTMock(mock_data.mock_prices):
        moving_average = statistics.calculate_moving_averages(
            ticker=ticker, start_date=start_date, end_date=end_date)

    if get_asset_type(ticker) == keys['ASSETS']['CRYPTO']:
        no_of_days = dater.days_between(start_date, end_date)
    else:
        no_of_days = dater.business_days_between(start_date, end_date)

    assert isinstance(moving_average, dict)
    assert len(list(moving_average.keys())) == no_of_days
    assert all(isinstance(averages, dict)
               for averages in moving_average.values())
    assert all(all(isinstance(average, float) for average in average_dict.values())
               for average_dict in moving_average.values())


@pytest.mark.parametrize("ticker,start_date,end_date", mock_data.service_price_cases)
def test_sample_of_returns(ticker, start_date, end_date):
    with HTTMock(mock_data.mock_prices):
        these_returns = statistics.get_sample_of_returns(ticker=ticker,
                                                         start_date=dater.parse(
                                                             start_date),
                                                         end_date=dater.parse(end_date))

    if get_asset_type(ticker) == keys['ASSETS']['CRYPTO']:
        no_of_days = dater.days_between(start_date, end_date)
    else:
        no_of_days = dater.business_days_between(start_date, end_date)

    assert isinstance(these_returns, list)
    assert all(isinstance(this_return, float) for this_return in these_returns)
    # subtract one because differencing price history loses one sample
    assert len(these_returns) == no_of_days - 1


@pytest.mark.parametrize('ticker,start_date,end_date', [
    ('ALLY', '2021-11-12', '2021-11-12'),
    ('BX', '2021-11-06', '2021-11-08')
])
def test_sample_of_returns_with_no_sample(ticker, start_date, end_date):
    with pytest.raises(Exception) as sample_error:
        statistics.get_sample_of_returns(
            ticker=ticker, start_date=start_date, end_date=end_date)
    assert sample_error.type == SampleSizeError


@pytest.mark.parametrize("ticker,start_date,end_date", mock_data.service_price_cases)
def test_standardized_sample_of_returns(ticker, start_date, end_date):
    with HTTMock(mock_data.mock_prices):
        these_returns = standardize(statistics.get_sample_of_returns(ticker=ticker,
                                                                     start_date=dater.parse(
                                                                         start_date),
                                                                     end_date=dater.parse(end_date)))

    if get_asset_type(ticker) == keys['ASSETS']['CRYPTO']:
        no_of_days = dater.days_between(start_date, end_date)
    else:
        no_of_days = dater.business_days_between(start_date, end_date)

    assert isinstance(these_returns, list)
    assert all(isinstance(this_return, float) for this_return in these_returns)
    # subtract one because differencing price history loses one sample
    assert len(these_returns) == no_of_days - 1
