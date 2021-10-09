from scrilla.static.constants import constants
from scrilla.static import keys
from scrilla.util import dater

def get_trading_period(asset_type: str) -> float:
    """
    Returns the value of one trading day measured in years of the asset_type passed in as an argument.

    Parameters
    ----------
    1. **asset_type**: ``str``
    
    A string that represents a type of tradeable asset. Types are statically accessible through the ` settings` variables: ASSET_EQUITY and ASSET_CRYPTO.
    """
    if asset_type == keys.keys['ASSETS']['CRYPTO']:
        return constants['ONE_TRADING_DAY']['CRYPTO']
    return constants['ONE_TRADING_DAY']['EQUITY']

def format_profiles(profiles: dict):
    profiles_format = []
    for key, value in profiles.items():
        holding = value
        holding['ticker'] = key
        profiles_format.append(holding)
    return profiles_format

def format_allocation(allocation, portfolio, investment=None):
    allocation_format = []

    if investment is not None:
        shares = portfolio.calculate_approximate_shares(x=allocation, total=investment)
        total = portfolio.calculate_actual_total(x=allocation, total=investment)

    annual_volatility = portfolio.volatility_function(x=allocation) 
    annual_return = portfolio.return_function(x=allocation)

    for j, item in enumerate(portfolio.tickers):
        holding = {}
        holding['ticker'] = item
        holding['allocation'] = round(allocation[j], constants['ACCURACY'])
        if investment is not None:
            holding['shares'] = float(shares[j])
        holding['annual_return'] = round(portfolio.mean_return[j], constants['ACCURACY']) 
        holding['annual_volatility'] = round(portfolio.sample_vol[j], constants['ACCURACY'])
        allocation_format.append(holding)

    json_format = {}
    json_format['holdings'] = allocation_format

    if investment is not None:
        json_format['total'] = float(total)
        
    json_format['portfolio_return'] = annual_return
    json_format['portfolio_volatility'] = annual_volatility
    
    return json_format

def format_frontier(portfolio, frontier, investment=None):
    json_format = []
    for i, item in enumerate(frontier):
        json_format.append(format_allocation(allocation=item, portfolio=portfolio, 
                                                            investment=investment))
    return json_format

def format_correlation_matrix(tickers, correlation_matrix):
    response = []
    for i, item in enumerate(tickers):
        # correlation_matrix[i][i]
        for j in range(i+1, len(tickers)):
            subresponse = {}
            subresponse[f'{item}_{tickers[j]}_correlation'] = correlation_matrix[j][i]
            response.append(subresponse)
    return response

# GUI FORMATTING
def format_allocation_profile_title(allocation, portfolio) -> str:
    port_return, port_volatility = portfolio.return_function(allocation), portfolio.volatility_function(allocation)
    formatted_result = "("+str(100*port_return)[:5]+"%, " + str(100*port_volatility)[:5]+"%)"
    formatted_result_title = "("
    for symbol in portfolio.tickers:
        if portfolio.tickers.index(symbol) != (len(portfolio.tickers) - 1):
            formatted_result_title += symbol+", "
        else:
            formatted_result_title += symbol + ") Portfolio Return-Risk Profile"
    whole_thing = formatted_result_title +" = "+formatted_result
    return whole_thing

# TODO: refactor this, along with scrilla.analysis.models.geometric.statistics.calculate_moving_averages
def format_moving_averages(tickers, averages_output):
    these_moving_averages, dates = averages_output

    response = {}
    for i, item in enumerate(tickers):
        ticker_str=f'{item}'
        MA_1_str, MA_2_str, MA_3_str = f'{ticker_str}_MA_1', f'{ticker_str}_MA_2', f'{ticker_str}_MA_3'    

        subresponse = {}
        if dates is None:
            subresponse[MA_1_str] = these_moving_averages[i][0]
            subresponse[MA_2_str] = these_moving_averages[i][1]
            subresponse[MA_3_str] = these_moving_averages[i][2]

        else:
            subsubresponse_1, subsubresponse_2, subsubresponse_3 = {}, {}, {}
    
            for j, this_item in enumerate(dates):
                date_str=dater.date_to_string(this_item)
                subsubresponse_1[date_str] = these_moving_averages[i][0][j]
                subsubresponse_2[date_str] = these_moving_averages[i][1][j]
                subsubresponse_3[date_str] = these_moving_averages[i][2][j]

            subresponse[MA_1_str] = subsubresponse_1
            subresponse[MA_2_str] = subsubresponse_2
            subresponse[MA_3_str] = subsubresponse_3

        response[ticker_str] = subresponse
    
    return response
