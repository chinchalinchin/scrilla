# Django Imports
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

# Server Imports
from core import settings
from api import parser
from data.models import EquityMarket, CryptoMarket, EquityTicker, CryptoTicker, Dividends, Economy, StatSymbol

# Application Imports
from app.objects.portfolio import Portfolio
from app.objects.cashflow import Cashflow
import app.statistics as statistics
import app.services as services
import app.optimizer as optimizer
import app.settings as app_settings
import app.markets as markets

# Utility Imports
import util.helper as helper
import util.plotter as plotter
import util.outputter as outputter

output = outputter.Logger("server.pynance_api.api.views", settings.LOG_LEVEL)

def risk_return(request):
    status, parsed_args_or_err_msg = parser.validate_request(request, ["GET"])

    if status in [400, 405]:
        return JsonResponse(data=parsed_args_or_err_msg, status=status, safe=False)

    tickers = parsed_args_or_err_msg['tickers']
    parsed_args = parsed_args_or_err_msg['parsed_args']

    response = {}
    profiles = []

    for i in range(len(tickers)):
        ticker_str = f'{tickers[i]}'
        output.debug(f'Calculating risk-return profile for {tickers[i]}')

        prices = parser.parse_args_into_market_queryset(ticker=tickers[i], parsed_args=parsed_args)

        if prices.count() == 0:
            output.debug(f'No prices found in database, passing query call to application.')
            profile = statistics.calculate_risk_return(ticker=tickers[i], start_date=parsed_args['start_date'], 
                                                        end_date=parsed_args['end_date'])

        else:
            output.debug(f'Prices found in database, passing result to application.')
            sample_prices = parser.market_queryset_to_list(price_models=prices)
            profile = statistics.calculate_risk_return(ticker=tickers[i], sample_prices=sample_prices)

        response[ticker_str] = profile

        if parsed_args['jpeg']:
            profiles.append(profile)

    if parsed_args['jpeg']:
        graph = plotter.plot_profiles(symbols=tickers, profiles=profiles, show=False)
        response = HttpResponse(content_type="image/png")
        graph.print_png(response)
        return response

    return JsonResponse(data=response, status=status, safe=False)

def optimize(request):
    status, parsed_args_or_err_msg = parser.validate_request(request, ["GET"])
    
    if status in [400, 405]:
        return JsonResponse(data=parsed_args_or_err_msg, status=status, safe=False)

    tickers = parsed_args_or_err_msg['tickers']
    parsed_args = parsed_args_or_err_msg['parsed_args']
    prices, sample_prices = {}, {}
    null_result = False

    # TODO: what is querysets.count() != each other?
    for ticker in tickers:
        prices[ticker] = parser.parse_args_into_market_queryset(ticker, parsed_args)
        if prices[ticker].count() == 0:
            null_result=True
            break
    
    if null_result:
        output.debug(f'No prices found in database, passing query call to application.')
        portfolio = Portfolio(tickers=tickers, start_date=parsed_args['start_date'], end_date=parsed_args['end_date'])
    else:
        output.debug(f'Prices found in database, passing query call to application.')
        for ticker in tickers:
            sample_prices[ticker] = parser.market_queryset_to_list(price_model=prices[ticker])[ticker]
        portfolio = Portfolio(tickers=tickers, sample_prices=sample_prices)  

    allocation = optimizer.optimize_portfolio_variance(portfolio=portfolio, target_return=parsed_args['target_return'])
    allocation = helper.round_array(array=allocation, decimals=4)

    response = {
        'portfolio_return' : portfolio.return_function(allocation),
        'portfolio_volatility': portfolio.volatility_function(allocation)
    }
    subresponse = {}

    for i in range(len(tickers)):
        allocation_string = f'{tickers[i]}_allocation'
        subresponse[allocation_string] = allocation[i]

    response['allocations'] = subresponse
    return JsonResponse(data=response, status=status, safe=False)

def efficient_frontier(request):
    status, parsed_args_or_err_msg = parser.validate_request(request, ["GET"])

    if status in [400, 405]:
        return JsonResponse(data=parsed_args_or_err_msg, status=status, safe=False)
    
    tickers = parsed_args_or_err_msg['tickers']
    parsed_args = parsed_args_or_err_msg['parsed_args']

    prices, sample_prices = {}, {}
    null_result = False

    # TODO: what is querysets.count() != each other?
    for ticker in tickers:
        prices[ticker] = parser.parse_args_into_market_queryset(ticker, parsed_args)
        if prices[ticker].count() == 0:
            null_result=True
            break

    if null_result:
        output.debug(f'No prices found in database, passing query to service.')
        portfolio = Portfolio(tickers=tickers, start_date=parsed_args['start_date'], end_date=parsed_args['end_date'])
    else:
        output.debug(f'Prices found in database, passing result to statistics.')
        for ticker in tickers:
            sample_prices[ticker] = parser.market_queryset_to_list(price_model=prices[ticker])[ticker]
        portfolio = Portfolio(tickers=tickers, sample_prices=sample_prices)  
        
    frontier = optimizer.calculate_efficient_frontier(portfolio=portfolio)

    response = {}
    for i in range(len(frontier)):
        subresponse, subsubresponse = {}, {}
        port_string =  f'portfolio_{i}'

        allocation = helper.round_array(array=frontier[i], decimals=4)
        subresponse['portfolio_return'] = helper.truncate(portfolio.return_function(allocation), 4)
        subresponse['portfolio_volatility'] = helper.truncate(portfolio.volatility_function(allocation), 4)

        for j in range(len(tickers)):
            allocation_string = f'{tickers[j]}_allocation'
            subsubresponse[allocation_string] = allocation[j]

        subresponse['allocation']=subsubresponse
        response[port_string] = subresponse
    
    if parsed_args['jpeg']:
        graph = plotter.plot_frontier(portfolio=portfolio, frontier=frontier, show=False)
        response = HttpResponse(content_type="image/png")
        graph.print_png(response)
        return response
    
    return JsonResponse(data=response, status=status, safe=False) 

# TODO: in future allow user to specify moving average periods through query parameters! 
def moving_averages(request):
    status, parsed_args_or_err_msg = parser.validate_request(request, ["GET"])

    if status in [400, 405]:
        return JsonResponse(data=parsed_args_or_err_msg, status=status, safe=False)

    tickers = parsed_args_or_err_msg['tickers']
    parsed_args = parsed_args_or_err_msg['parsed_args']

    prices, sample_prices = {}, {}
    null_result = False

    # TODO: what is querysets.count() != each other?
    for ticker in tickers:
        prices[ticker] = parser.parse_args_into_queryset(ticker, parsed_args)
        if prices[ticker].count() == 0:
            null_result=True
            break

    if null_result:
        output.debug(f'No prices found in database, passing query to service.')
        averages_output = statistics.calculate_moving_averages(tickers=tickers, start_date=parsed_args['start_date'],
                                                                end_date=parsed_args['end_date'])
    else: 
        output.debug(f'Prices found in database, passing result to statistics.')
        for ticker in tickers:
            sample_prices[ticker] = parser.market_queryset_to_list(price_model=prices[ticker])[ticker]
        averages_output = statistics.calculate_moving_averages(tickers=tickers, sample_prices=sample_prices)

    moving_averages, dates = averages_output

    response = {}
    for i in range(len(tickers)):
        ticker_str=f'{tickers[i]}'
        MA_1_str, MA_2_str, MA_3_str = f'{ticker_str}_MA_1', f'{ticker_str}_MA_2', f'{ticker_str}_MA_3'    

        subresponse = {}
        if parsed_args['start_date'] is None and parsed_args['end_date'] is None:
            subresponse[MA_1_str] = moving_averages[i][0]
            subresponse[MA_2_str] = moving_averages[i][1]
            subresponse[MA_3_str] = moving_averages[i][2]

        else:
            subsubresponse_1, subsubresponse_2, subsubresponse_3 = {}, {}, {}
    
            for j in range(len(dates)):
                date_str=helper.date_to_string(dates[j])
                subsubresponse_1[date_str] = moving_averages[i][0][j]
                subsubresponse_2[date_str] = moving_averages[i][1][j]
                subsubresponse_3[date_str] = moving_averages[i][2][j]

            subresponse[MA_1_str] = subsubresponse_1
            subresponse[MA_2_str] = subsubresponse_2
            subresponse[MA_3_str] = subsubresponse_3

        response[ticker_str] = subresponse

    if parsed_args['jpeg']:
        periods = [app_settings.MA_1_PERIOD, app_settings.MA_2_PERIOD, app_settings.MA_3_PERIOD]
        graph = plotter.plot_moving_averages(symbols=tickers, averages_output=averages_output, periods=periods,
                                                show=False)
        response = HttpResponse(content_type="image/png")
        graph.print_png(response)
        return response

    return JsonResponse(data = response, status=status, safe=False)

def discount_dividend(request):
    status, parsed_args_or_err_msg = parser.validate_request(request, ["GET"])

    if status in [400, 405]:
        return JsonResponse(data=parsed_args_or_err_msg, status=status, safe=False)

    
    tickers = parsed_args_or_err_msg['tickers']
    parsed_args = parsed_args_or_err_msg['parsed_args']

    response = {}
    cashflow_to_plot = None
    for ticker in tickers:
        if parsed_args['discount_rate'] is None:
            discount_rate = markets.cost_of_equity(ticker)
        else:
            discount_rate = parsed_args['discount_rate']

        dividends = parser.parse_args_into_dividend_queryset(ticker=ticker, parsed_args=parsed_args)

        if dividends.count() == 0:
            output.debug(f'No dividends found in database, passing query call to application.')
            dividends = services.query_service_for_dividend_history(ticker=ticker)
        else:
            output.debug(f'Dividends found in database, passing result to application.')
            dividends = parser.dividend_queryset_to_list(dividend_set=dividends)

        present_value = Cashflow(sample=dividends,discount_rate=discount_rate).calculate_net_present_value()

        # Save first ticker's dividend cash flow history to pass to plotter in case the JPEG argument 
        #   has been provided through the URL's query parameters.
        if cashflow_to_plot is None:
            cashflow_to_plot = Cashflow(sample=dividends,discount_rate=discount_rate)

        if present_value:
            response[ticker] = {
                'discount_dividend_model': present_value
            }
        else:
            response[ticker] = {
                'error' : 'discount_dividend_model cannot be computed.'
            }
    
    if parsed_args['jpeg']:
        graph = plotter.plot_cashflow(ticker=tickers[0], cashflow=cashflow_to_plot, show=False)
        response = HttpResponse(content_type="image/png")
        graph.print_png(response)
        return response

    return JsonResponse(data=response, status=status, safe=False)