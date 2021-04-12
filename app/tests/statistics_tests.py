import sys, os
import numpy

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_DIR)

from app import statistics, settings, services, markets
from util import outputter, helper

rolling_x_y_1 = [[1, 3, 5, 2, 6, 10],[4, 5, 3, 6, 2, 8]]
rolling_x_y_2 = [[3, 5, 2, 6, 10, 8], [5, 3, 6, 2, 8, 5]]
rolling_x_y_3 = [[5, 2, 6, 10, 8, 2], [3, 6, 2, 8, 5, 10]]
rolling_x_y_4 = [[2, 6, 10, 8, 2, 3], [6, 2, 8, 5, 10, 9]]
x_y_data = [[1, 2, 3, 4, 5, 6, 7],[20, 19, 23, 20, 26, 22, 30]]
test_dates = ["2021-03-29", "2021-01-13", "2020-10-20", "2019-12-10"]
test_tickers = ["ALLY", "BX", "TWTR"]

def regression_test():
    # REGRESSION CALCULATIONS
    correl = statistics.sample_correlation(x=x_y_data[0], y=x_y_data[1])
    beta = statistics.regression_beta(x=x_y_data[0],y=x_y_data[1])
    alpha = statistics.regression_alpha(x=x_y_data[0],y=x_y_data[1])
    
    # TEST RESULTS
    outputter.print_line()
    outputter.center("Regression Testing")
    outputter.print_line()
    outputter.title_line('Test Results')
    outputter.print_line()
    outputter.scalar_result(calculation='correct correlation', result=0.764852927, currency=False)
    outputter.scalar_result(calculation='sample_correlation(x, y)',  result=correl, currency=False)
    outputter.print_line()
    outputter.scalar_result(calculation='correct regression slope', result= 1.39286, currency=False)
    outputter.scalar_result(calculation='regression_beta(x,y)',  result=beta, currency=False)
    outputter.print_line()
    outputter.scalar_result(calculation='correct regression intercept',  result=17.28571, currency=False)
    outputter.scalar_result(calculation='regression_alpha(x,y)',  result=alpha, currency=False)
    outputter.print_line()

def rolling_recursion_test():
    length = len(rolling_x_y_1[0])
    
    # ACTUAL MEANS
    x_mean_1 = statistics.sample_mean(x=rolling_x_y_1[0])
    x_mean_2 = statistics.sample_mean(x=rolling_x_y_2[0])
    x_mean_3 = statistics.sample_mean(x=rolling_x_y_3[0])
    x_mean_4 = statistics.sample_mean(x=rolling_x_y_4[0])
    y_mean_1 = statistics.sample_mean(x=rolling_x_y_1[1])
    y_mean_2 = statistics.sample_mean(x=rolling_x_y_2[1])
    y_mean_3 = statistics.sample_mean(x=rolling_x_y_3[1])
    y_mean_4 = statistics.sample_mean(x=rolling_x_y_4[1])

    # RECURSIVE MEANS
    recursive_x_mean_2 = statistics.recursive_mean(xbar_previous=x_mean_1,new_obs=8, lost_obs=1, n=length)
    recursive_x_mean_3 = statistics.recursive_mean(xbar_previous=x_mean_2, new_obs=2, lost_obs=3, n=length)
    recursive_x_mean_4 = statistics.recursive_mean(xbar_previous=x_mean_3, new_obs=3, lost_obs=5, n=length)
    recursive_y_mean_2 = statistics.recursive_mean(xbar_previous=y_mean_1, new_obs=5, lost_obs=4, n=length)
    recursive_y_mean_3 = statistics.recursive_mean(xbar_previous=y_mean_2, new_obs=10, lost_obs=5, n=length)
    recursive_y_mean_4 = statistics.recursive_mean(xbar_previous=y_mean_3, new_obs=9, lost_obs=3, n=length)

    # ACTUAL VARIANCES
    var_1 = statistics.sample_variance(x=rolling_x_y_1[0])
    var_2 = statistics.sample_variance(x=rolling_x_y_2[0])
    var_3 = statistics.sample_variance(x=rolling_x_y_3[0])
    var_4 = statistics.sample_variance(x=rolling_x_y_4[0])

    # RECURSIVE VARIANCES
    recursive_var_2 = statistics.recursive_variance(var_previous=var_1, xbar_previous=x_mean_1, new_obs=8, lost_obs=1, n=length)
    recursive_var_3 = statistics.recursive_variance(var_previous=var_2, xbar_previous=recursive_x_mean_2, new_obs=2, lost_obs=3, n=length)
    recursive_var_4 = statistics.recursive_variance(var_previous=var_3, xbar_previous=recursive_x_mean_3, new_obs=3, lost_obs=5, n=length)

    # ACTUAL COVARIANCES
    covar_1 = statistics.sample_covariance(x=rolling_x_y_1[0], y=rolling_x_y_1[1])
    covar_2 = statistics.sample_covariance(x=rolling_x_y_2[0], y=rolling_x_y_2[1])
    covar_3 = statistics.sample_covariance(x=rolling_x_y_3[0], y=rolling_x_y_3[1])
    covar_4 = statistics.sample_covariance(x=rolling_x_y_4[0], y=rolling_x_y_4[1])

    # RECURSIVE COVARIANCES
    recursive_covar_2 = statistics.recursive_covariance(covar_previous=covar_1, new_x_obs=8, lost_x_obs=1, previous_x_bar= x_mean_1,
                                                        new_y_obs=5, lost_y_obs=4, previous_y_bar=y_mean_1, n=length)
    recursive_covar_3 = statistics.recursive_covariance(covar_previous=covar_2, new_x_obs=2, lost_x_obs=3, previous_x_bar = x_mean_2,
                                                        new_y_obs=10, lost_y_obs=5, previous_y_bar = y_mean_2, n=length)
    recursive_covar_4 = statistics.recursive_covariance(covar_previous=covar_3, new_x_obs=3, lost_x_obs=5, previous_x_bar=x_mean_3, 
                                                        new_y_obs=9, lost_y_obs=3, previous_y_bar=y_mean_3, n=length)

    # TEST RESULTS
    outputter.print_line()
    outputter.center("Rolling Sample Statistics Recursion Testing")
    outputter.print_line()
    outputter.title_line('Test Results')
    outputter.print_line()
    outputter.scalar_result(calculation="Actual Mean 2", result=x_mean_2, currency=False)
    outputter.scalar_result(calculation="Recursive Mean 2", result=recursive_x_mean_2, currency=False)
    outputter.print_line()
    outputter.scalar_result(calculation="Actual Y Mean 2", result=y_mean_2, currency=False)
    outputter.scalar_result(calculation="Recursive Y Mean 2", result=recursive_y_mean_2, currency=False)
    outputter.print_line()
    outputter.scalar_result(calculation="Actual Variance 2", result=var_2, currency=False)
    outputter.scalar_result(calculation="Recursive Variance 2", result=recursive_var_2, currency=False)
    outputter.print_line()
    outputter.scalar_result(calculation="Actual Covariance 2", result=covar_2, currency=False)
    outputter.scalar_result(calculation="Recursive Covariance 2", result=recursive_covar_2, currency=False)
    outputter.print_line()
    outputter.scalar_result(calculation="Actual Mean 3", result=x_mean_3, currency=False)
    outputter.scalar_result(calculation="Recursive Mean 3", result=recursive_x_mean_3, currency=False)
    outputter.print_line()
    outputter.scalar_result(calculation="Actual Y Mean 3", result=y_mean_3, currency=False)
    outputter.scalar_result(calculation="Recursive Y Mean 3", result=recursive_y_mean_3, currency=False)
    outputter.print_line()
    outputter.scalar_result(calculation="Actual Variance 3", result=var_3, currency=False)
    outputter.scalar_result(calculation="Recursive Variance 3", result=recursive_var_3, currency=False)
    outputter.print_line()
    outputter.scalar_result(calculation="Actual Covariance 3", result=covar_3, currency=False)
    outputter.scalar_result(calculation="Recursive Covariance 3", result=recursive_covar_3, currency=False)
    outputter.print_line()
    outputter.scalar_result(calculation="Actual Mean 4", result=x_mean_4, currency=False)
    outputter.scalar_result(calculation="Recursive Mean 4", result=recursive_x_mean_4, currency=False)
    outputter.print_line()
    outputter.scalar_result(calculation="Actual Y Mean 4", result=y_mean_4, currency=False)
    outputter.scalar_result(calculation="Recursive Y Mean 4", result=recursive_y_mean_4, currency=False)
    outputter.print_line()
    outputter.scalar_result(calculation="Actual Variance 4", result=var_4, currency=False)
    outputter.scalar_result(calculation="Recursive Variance 4", result=recursive_var_4, currency=False)
    outputter.print_line()
    outputter.scalar_result(calculation="Actual Covariance 4", result=covar_4, currency=False)
    outputter.scalar_result(calculation="Recursive Covariance 4", result=recursive_covar_4, currency=False)
    outputter.print_line()

def rolling_recursion_tests_with_financial_data():
    trading_period = markets.get_trading_period(asset_type=settings.ASSET_EQUITY)
    outputter.print_line()
    outputter.center('Rolling Recursive Risk Profile Test')
    outputter.print_line()
    outputter.title_line('Test Results')
    outputter.print_line()

    for ticker in test_tickers:
        for date in test_dates:
            end_date = helper.parse_date_string(date)
            start_date = helper.decrement_date_by_business_days(start_date=end_date, 
                                                                business_days=settings.DEFAULT_ANALYSIS_PERIOD)
            previous_end_date = helper.decrement_date_by_business_days(start_date=end_date, 
                                                                        business_days=1)
            previous_start_date = helper.decrement_date_by_business_days(start_date=start_date, 
                                                                            business_days=1)
            
            prices = services.get_daily_price_history(ticker=ticker, start_date=previous_start_date, 
                                                        end_date=end_date)
            previous_prices = dict(prices)
            new_prices = dict(prices)
                # TODO: what is end_date and previous_start_date are holidays/weekends?
                    # They can't be because decrement_by_business_days only returns business days.
            del previous_prices[helper.date_to_string(end_date)]
            del new_prices[helper.date_to_string(previous_start_date)]
            
            end_date_price = services.parse_price_from_date(prices=prices,
                                                            date=helper.date_to_string(end_date), 
                                                            asset_type=settings.ASSET_EQUITY)
            previous_end_date_price = services.parse_price_from_date(prices=prices, 
                                                            date=helper.date_to_string(previous_end_date), 
                                                            asset_type=settings.ASSET_EQUITY)
            start_date_price = services.parse_price_from_date(prices=prices,
                                                            date=helper.date_to_string(start_date), 
                                                            asset_type=settings.ASSET_EQUITY)
            previous_start_date_price = services.parse_price_from_date(prices=prices,
                                                            date=helper.date_to_string(previous_start_date),
                                                            asset_type=settings.ASSET_EQUITY)

            print('end_date, previous_end_date, start_date, previous_start_date and prices')
            print(end_date, previous_end_date, start_date, previous_start_date)
            print(end_date_price, previous_end_date_price, start_date_price, previous_start_date_price)

            new_return = numpy.log(float(end_date_price)/float(previous_end_date_price))/trading_period
            lost_return = numpy.log(float(start_date_price)/float(previous_start_date_price))/trading_period
            new_mod_return = new_return*numpy.sqrt(trading_period)
            lost_mod_return = lost_return*numpy.sqrt(trading_period)

            old_profile = statistics.calculate_risk_return(ticker=ticker, sample_prices=previous_prices)
            old_mod_return = old_profile['annual_return']*numpy.sqrt(trading_period)

            new_actual_profile = statistics.calculate_risk_return(ticker=ticker, sample_prices=new_prices)

            new_recursive_profile = {}
            new_recursive_profile['annual_return'] = statistics.recursive_mean(xbar_previous=old_profile['annual_return'],
                                                                                new_obs=new_return,
                                                                                lost_obs=lost_return)
            new_recursive_profile['annual_volatility'] = statistics.recursive_variance(var_previous=old_profile['annual_volatility'],
                                                                                        xbar_previous=old_mod_return,
                                                                                        new_obs=new_mod_return,
                                                                                        lost_obs=lost_mod_return)
            new_recursive_profile['annual_volatility'] = numpy.sqrt(new_recursive_profile['annual_volatility'])

            outputter.scalar_result(calculation=f'{ticker}_return({date})_actual', result=new_actual_profile['annual_return'],currency=False)
            outputter.scalar_result(calculation=f'{ticker}_return({date})_recursive', result=new_recursive_profile['annual_return'], currency=False)
            outputter.scalar_result(calculation=f'{ticker}_vol({date})_actual', result=new_actual_profile['annual_volatility'], currency=False)
            outputter.scalar_result(calculation=f'{ticker}_vol({date})_recursive', result=new_recursive_profile['annual_volatility'], currency=False)
            # calculate rolling recursive end_date sample return
            # calculate actual end_date sample return

# TODO: need to test service retrieval through command line to be confident it's returning the correct info.

if __name__ == "__main__":
    regression_test()
    rolling_recursion_test()
    rolling_recursion_tests_with_financial_data()