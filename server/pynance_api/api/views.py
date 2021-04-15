# Django Imports
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

# Server Imports
from core import settings
from api import parser
from data import analyzer, cache, models

# Application Imports
import app.settings as app_settings
from app.objects.portfolio import Portfolio
from app.objects.cashflow import Cashflow
import app.statistics as statistics
import app.services as services
import app.optimizer as optimizer
import app.markets as markets
import app.files as files

# Utility Imports
import util.helper as helper
import util.plotter as plotter
import util.outputter as outputter

output = outputter.Logger("server.pynance_api.api.views", settings.LOG_LEVEL)

def risk_return(request):
    status, parsed_args_or_err_msg = parser.validate_request(request, ["GET"])

    if status in [400, 405]:
        return JsonResponse(data=parsed_args_or_err_msg, status=status, safe=False)

    tickers, parsed_args = parsed_args_or_err_msg['tickers'], parsed_args_or_err_msg['parsed_args']
    market_profile, risk_free_rate = analyzer.initialize_market_info(parsed_args=parsed_args)
    response, profiles = {}, []

    for i in range(len(tickers)):
        profile, prices = {}, {}
        ticker_str = f'{tickers[i]}'
        output.debug(f'Calculating risk-return profile for {tickers[i]}.')

        output.debug(f'Checking for {tickers[i]} profile in the database cache.')
        profile = cache.check_for_profile(ticker=tickers[i], start_date=parsed_args['start_date'],
                                                    end_date=parsed_args['end_date'])
        if profile is not None:
            output.debug(f'Found profile in database cache, halting calculation.')
            response[i] = profile
            if parsed_args['jpeg']:
                profiles.append(profile)
            continue # halt this iteration of loop if profile cache found
        else:
            output.debug(f'No profile found in database cache, proceeding with calculation.')
            profile = {}

        analyzer.market_queryset_gap_analysis(symbol=tickers[i],start_date=parsed_args['start_date'],
                                                end_date=parsed_args['end_date'])

        prices[tickers[i]] = parser.parse_args_into_market_queryset(ticker=tickers[i], parsed_args=parsed_args)
        prices[app_settings.MARKET_PROXY] = parser.parse_args_into_market_queryset(ticker=app_settings.MARKET_PROXY,
                                                                                    parsed_args=parsed_args)
        stats = statistics.calculate_risk_return(ticker=tickers[i], sample_prices=prices[tickers[i]])
        
        correlation = cache.check_for_correlation(this_ticker_1=tickers[i], this_ticker_2=app_settings.MARKET_PROXY,
                                                    start_date=parsed_args['start_date'], end_date=parsed_args['end_date'])
        if correlation is None:
            correlation = statistics.calculate_ito_correlation(ticker_1=tickers[i], 
                                                                ticker_2=app_settings.MARKET_PROXY, 
                                                                sample_prices=prices)
            cache.save_correlation(this_ticker_1=tickers[i], this_ticker_2=app_settings.MARKET_PROXY, 
                                    correlation=correlation, start_date=parsed_args['start_date'], 
                                    end_date=parsed_args['end_date'])
        profile['ticker'] = ticker_str
        profile['annual_return'], profile['annual_volatility'] = stats['annual_return'], stats['annual_volatility']
        profile['sharpe_ratio'] = markets.sharpe_ratio(ticker=tickers[i], start_date=parsed_args['start_date'],
                                                        end_date=parsed_args['end_date'], ticker_profile = profile, 
                                                        risk_free_rate=risk_free_rate)
 
        profile['asset_beta'] = markets.market_beta(ticker=tickers[i], start_date=parsed_args['start_date'],
                                                        end_date=parsed_args['end_date'], market_profile=market_profile,
                                                        market_correlation=correlation, sample_prices=prices)
        
        cache.save_profile(profile=profile,start_date=parsed_args['start_date'], end_date=parsed_args['end_date'])

        response[i] = profile

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

    tickers, parsed_args = parsed_args_or_err_msg['tickers'], parsed_args_or_err_msg['parsed_args']
    prices = {}

    for ticker in tickers:
        analyzer.market_queryset_gap_analysis(symbol=ticker,start_date=parsed_args['start_date'],
                                                end_date=parsed_args['end_date'])
        prices[ticker] = parser.parse_args_into_market_queryset(ticker, parsed_args)

    correlation_matrix = cache.build_correlation_matrix(these_tickers=tickers, start_date=parsed_args['start_date'],
                                                        end_date=parsed_args['end_date'], sample_prices=prices)
    # TODO: 
    portfolio = Portfolio(tickers=tickers, sample_prices=prices, correlation_matrix=correlation_matrix)    
    if parsed_args['sharpe_ratio'] is None:
        allocation = optimizer.optimize_portfolio_variance(portfolio=portfolio, target_return=parsed_args['target_return'])
    else:
        allocation = optimizer.maximize_sharpe_ratio(portfolio=portfolio, target_return=parsed_args['target_return'])

    allocation = helper.round_array(array=allocation, decimals=5)
    response = files.format_allocation(allocation=allocation, portfolio=portfolio, investment=parsed_args['investment'])
    return JsonResponse(data=response, status=status, safe=False)

def efficient_frontier(request):
    status, parsed_args_or_err_msg = parser.validate_request(request, ["GET"])

    if status in [400, 405]:
        return JsonResponse(data=parsed_args_or_err_msg, status=status, safe=False)
    
    tickers, parsed_args = parsed_args_or_err_msg['tickers'], parsed_args_or_err_msg['parsed_args']
    prices = {}

    for ticker in tickers:
        analyzer.market_queryset_gap_analysis(symbol=ticker,start_date=parsed_args['start_date'],
                                                end_date=parsed_args['end_date'])
        prices[ticker] = parser.parse_args_into_market_queryset(ticker, parsed_args)

    correlation_matrix = cache.build_correlation_matrix(these_tickers=tickers, start_date=parsed_args['start_date'],
                                                        end_date=parsed_args['end_date'], sample_prices=prices)
    portfolio = Portfolio(tickers=tickers, sample_prices=prices, correlation_matrix=correlation_matrix)    
    frontier = optimizer.calculate_efficient_frontier(portfolio=portfolio)
    
    if parsed_args['jpeg']:
        graph = plotter.plot_frontier(portfolio=portfolio, frontier=frontier, show=False)
        response = HttpResponse(content_type="image/png")
        graph.print_png(response)
        return response

    response = files.format_frontier(portfolio=portfolio,frontier=frontier,investment=parsed_args['investment'])
    return JsonResponse(data=response, status=status, safe=False) 

# TODO: in future allow user to specify moving average periods through query parameters! 
def moving_averages(request):
    status, parsed_args_or_err_msg = parser.validate_request(request, ["GET"])

    if status in [400, 405]:
        return JsonResponse(data=parsed_args_or_err_msg, status=status, safe=False)

    tickers, parsed_args = parsed_args_or_err_msg['tickers'], parsed_args_or_err_msg['parsed_args']
    prices = {}


    for ticker in tickers:
        analyzer.market_queryset_gap_analysis(symbol=ticker,start_date=parsed_args['start_date'],
                                                end_date=parsed_args['end_date'])
        prices[ticker] = parser.parse_args_into_market_queryset(ticker, parsed_args)
    
    averages_output = statistics.calculate_moving_averages(tickers=tickers, sample_prices=sample_prices)

    if parsed_args['jpeg']:
        periods = [app_settings.MA_1_PERIOD, app_settings.MA_2_PERIOD, app_settings.MA_3_PERIOD]
        graph = plotter.plot_moving_averages(symbols=tickers, averages_output=averages_output, periods=periods,
                                                show=False)
        response = HttpResponse(content_type="image/png")
        graph.print_png(response)
        return response
        
    response = files.format_moving_averages(tickers=tickers, averages_output=averages_output)
    return JsonResponse(data = response, status=status, safe=False)

def discount_dividend(request):
    status, parsed_args_or_err_msg = parser.validate_request(request, ["GET"])

    if status in [400, 405]:
        return JsonResponse(data=parsed_args_or_err_msg, status=status, safe=False)

    tickers, parsed_args = parsed_args_or_err_msg['tickers'], parsed_args_or_err_msg['parsed_args']
    response, cashflow_to_plot = {}, None

    for ticker in tickers:
        if parsed_args['discount_rate'] is None:
            discount_rate = markets.cost_of_equity(ticker)
        else:
            discount_rate = parsed_args['discount_rate']

        analyzer.dividend_queryset_gap_analysis(symbol=ticker)
        dividends = parser.parse_args_into_dividend_queryset(ticker=ticker, parsed_args=parsed_args)
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
                'error' : 'discount_dividend_model cannot be computed for this equity.'
            }
    
    if parsed_args['jpeg']:
        graph = plotter.plot_cashflow(ticker=tickers[0], cashflow=cashflow_to_plot, show=False)
        response = HttpResponse(content_type="image/png")
        graph.print_png(response)
        return response

    return JsonResponse(data=response, status=status, safe=False)