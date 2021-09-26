import sys, os
import numpy

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_DIR)

from scrilla import settings, services, static
from scrilla.util import outputter, helper
import scrilla.analysis.estimators as estimators
import scrilla.analysis.models.geometric.statistics as statistics

rolling_x_y_1 = [[1, 3, 5, 2, 6, 10],[4, 5, 3, 6, 2, 8]]
rolling_x_y_2 = [[3, 5, 2, 6, 10, 8], [5, 3, 6, 2, 8, 5]]
rolling_x_y_3 = [[5, 2, 6, 10, 8, 2], [3, 6, 2, 8, 5, 10]]
rolling_x_y_4 = [[2, 6, 10, 8, 2, 3], [6, 2, 8, 5, 10, 9]]
x_y_data = [[1, 2, 3, 4, 5, 6, 7],[20, 19, 23, 20, 26, 22, 30]]
x_y_correl, x_y_beta, x_y_alpha = 0.764852927, 1.39286, 17.28571
test_dates = ["2021-03-29", "2020-10-20", "2019-12-10"]
test_tickers = ["ALLY", "BX"]
lots = [ 12, 32, 34, 11, 23, 44, 53, 25, 24, 31, 35, 36]

def percentile_test():
    print('data : ',x_y_data[1])
    twenty_fifth = estimators.sample_percentile(data=x_y_data[1], percentile=0.25)
    fiftieth = estimators.sample_percentile(data=x_y_data[1], percentile=0.5)
    seventy_fifth = estimators.sample_percentile(data=x_y_data[1], percentile=0.75)
    ninetieth = estimators.sample_percentile(data=x_y_data[1], percentile=0.90)

    outputter.print_line()
    outputter.scalar_result(calculation='25th percentile', result = twenty_fifth, currency=False)
    outputter.scalar_result(calculation='50th percentile', result = fiftieth, currency=False)
    outputter.scalar_result(calculation='75th percentile', result = seventy_fifth, currency=False)
    outputter.scalar_result(calculation='90th percentile', result = ninetieth, currency=False)
    outputter.print_line()

    print('data : ', lots)
    twenty_fifth = estimators.sample_percentile(data=lots, percentile=0.25)
    fiftieth = estimators.sample_percentile(data=lots, percentile=0.5)
    seventy_fifth = estimators.sample_percentile(data=lots, percentile=0.75)
    ninetieth = estimators.sample_percentile(data=lots, percentile=0.90)

    outputter.print_line()
    outputter.scalar_result(calculation='25th percentile', result = twenty_fifth, currency=False)
    outputter.scalar_result(calculation='50th percentile', result = fiftieth, currency=False)
    outputter.scalar_result(calculation='75th percentile', result = seventy_fifth, currency=False)
    outputter.scalar_result(calculation='90th percentile', result = ninetieth, currency=False)
    outputter.print_line()


def simple_regression_test():
    # REGRESSION CALCULATIONS
    correl = estimators.sample_correlation(x=x_y_data[0], y=x_y_data[1])
    beta = estimators.simple_regression_beta(x=x_y_data[0],y=x_y_data[1])
    alpha = estimators.simple_regression_alpha(x=x_y_data[0],y=x_y_data[1])
    
    # TEST RESULTS
    outputter.scalar_result(calculation='correct correlation', result=x_y_correl, currency=False)
    outputter.scalar_result(calculation='sample_correlation(x, y)',  result=correl, currency=False)
    outputter.print_line()
    outputter.scalar_result(calculation='correct regression slope', result=x_y_beta, currency=False)
    outputter.scalar_result(calculation='simple_regression_beta(x,y)',  result=beta, currency=False)
    outputter.print_line()
    outputter.scalar_result(calculation='correct regression intercept',  result=x_y_alpha, currency=False)
    outputter.scalar_result(calculation='simple_regression_alpha(x,y)',  result=alpha, currency=False)
    outputter.print_line()

def rolling_recursion_test():
    length = len(rolling_x_y_1[0])
    
    # ACTUAL MEANS
    x_mean_1 = estimators.sample_mean(x=rolling_x_y_1[0])
    x_mean_2 = estimators.sample_mean(x=rolling_x_y_2[0])
    x_mean_3 = estimators.sample_mean(x=rolling_x_y_3[0])
    x_mean_4 = estimators.sample_mean(x=rolling_x_y_4[0])
    y_mean_1 = estimators.sample_mean(x=rolling_x_y_1[1])
    y_mean_2 = estimators.sample_mean(x=rolling_x_y_2[1])
    y_mean_3 = estimators.sample_mean(x=rolling_x_y_3[1])
    y_mean_4 = estimators.sample_mean(x=rolling_x_y_4[1])

    # RECURSIVE MEANS
    recursive_x_mean_2 = estimators.recursive_rolling_mean(xbar_previous=x_mean_1, new_obs=rolling_x_y_2[0][-1], 
                                                    lost_obs=rolling_x_y_1[0][0], n=length)
    recursive_x_mean_3 = estimators.recursive_rolling_mean(xbar_previous=x_mean_2, new_obs=rolling_x_y_3[0][-1], 
                                                    lost_obs=rolling_x_y_2[0][0], n=length)
    recursive_x_mean_4 = estimators.recursive_rolling_mean(xbar_previous=x_mean_3, new_obs=rolling_x_y_4[0][-1], 
                                                    lost_obs=rolling_x_y_3[0][0], n=length)
    recursive_y_mean_2 = estimators.recursive_rolling_mean(xbar_previous=y_mean_1, new_obs=rolling_x_y_2[1][-1], 
                                                    lost_obs=rolling_x_y_1[1][0], n=length)
    recursive_y_mean_3 = estimators.recursive_rolling_mean(xbar_previous=y_mean_2, new_obs=rolling_x_y_3[1][-1], 
                                                    lost_obs=rolling_x_y_2[1][0], n=length)
    recursive_y_mean_4 = estimators.recursive_rolling_mean(xbar_previous=y_mean_3, new_obs=rolling_x_y_4[1][-1], 
                                                    lost_obs=rolling_x_y_3[1][0], n=length)

    # ACTUAL VARIANCES
    var_1 = estimators.sample_variance(x=rolling_x_y_1[0])
    var_2 = estimators.sample_variance(x=rolling_x_y_2[0])
    var_3 = estimators.sample_variance(x=rolling_x_y_3[0])
    var_4 = estimators.sample_variance(x=rolling_x_y_4[0])

    # RECURSIVE VARIANCES
    recursive_var_2 = estimators.recursive_rolling_variance(var_previous=var_1, xbar_previous=x_mean_1, new_obs=rolling_x_y_2[0][-1], 
                                                    lost_obs=rolling_x_y_1[0][0], n=length)
    recursive_var_3 = estimators.recursive_rolling_variance(var_previous=var_2, xbar_previous=recursive_x_mean_2, new_obs=rolling_x_y_3[0][-1], 
                                                    lost_obs=rolling_x_y_2[0][0], n=length)
    recursive_var_4 = estimators.recursive_rolling_variance(var_previous=var_3, xbar_previous=recursive_x_mean_3, new_obs=rolling_x_y_4[0][-1], 
                                                    lost_obs=rolling_x_y_3[0][0], n=length)

    # ACTUAL COVARIANCES
    covar_1 = estimators.sample_covariance(x=rolling_x_y_1[0], y=rolling_x_y_1[1])
    covar_2 = estimators.sample_covariance(x=rolling_x_y_2[0], y=rolling_x_y_2[1])
    covar_3 = estimators.sample_covariance(x=rolling_x_y_3[0], y=rolling_x_y_3[1])
    covar_4 = estimators.sample_covariance(x=rolling_x_y_4[0], y=rolling_x_y_4[1])

    # RECURSIVE COVARIANCES
    recursive_covar_2 = estimators.recursive_rolling_covariance(covar_previous=covar_1, new_x_obs=rolling_x_y_2[0][-1], 
                                                        lost_x_obs=rolling_x_y_1[0][0], previous_x_bar= x_mean_1,
                                                        new_y_obs=rolling_x_y_2[1][-1], lost_y_obs=rolling_x_y_1[1][0], 
                                                        previous_y_bar=y_mean_1, n=length)
    recursive_covar_3 = estimators.recursive_rolling_covariance(covar_previous=covar_2, new_x_obs=rolling_x_y_3[0][-1], 
                                                        lost_x_obs=rolling_x_y_2[0][0], previous_x_bar = x_mean_2,
                                                        new_y_obs=rolling_x_y_3[1][-1], lost_y_obs=rolling_x_y_2[1][0],
                                                        previous_y_bar = y_mean_2, n=length)
    recursive_covar_4 = estimators.recursive_rolling_covariance(covar_previous=covar_3, new_x_obs=rolling_x_y_4[0][-1], 
                                                        lost_x_obs=rolling_x_y_3[0][0], previous_x_bar=x_mean_3, 
                                                        new_y_obs=rolling_x_y_4[1][-1], lost_y_obs=rolling_x_y_3[1][0], 
                                                        previous_y_bar=y_mean_3, n=length)

    # TEST RESULTS
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
    trading_period = static.get_trading_period(asset_type=static.keys['ASSETS']['EQUITY'])

    for ticker in test_tickers:
        for date in test_dates:
            start_date = helper.decrement_date_string_by_business_days(start_date_string=date, 
                                                                business_days=settings.DEFAULT_ANALYSIS_PERIOD)
            previous_end_date = helper.decrement_date_string_by_business_days(start_date_string=date, 
                                                                        business_days=1)
            previous_start_date = helper.decrement_date_string_by_business_days(start_date_string=start_date, 
                                                                            business_days=1)
            
            prices = services.get_daily_price_history(ticker=ticker, 
                                                        start_date=helper.parse_date_string(previous_start_date), 
                                                        end_date=helper.parse_date_string(date), 
                                                        asset_type=static.keys['ASSETS']['EQUITY'])
            previous_prices = dict(prices)
            new_prices = dict(prices)
            del previous_prices[date]
            del new_prices[previous_start_date]
            
            end_date_price = prices[date][static.keys['PRICES']['CLOSE']]
            previous_end_date_price = prices[previous_end_date][static.keys['PRICES']['CLOSE']]
            start_date_price = prices[start_date][static.keys['PRICES']['CLOSE']]
            previous_start_date_price = prices[start_date][static.keys['PRICES']['CLOSE']]

            new_return = numpy.log(float(end_date_price)/float(previous_end_date_price))/trading_period
            lost_return = numpy.log(float(start_date_price)/float(previous_start_date_price))/trading_period
            new_mod_return = new_return*numpy.sqrt(trading_period)
            lost_mod_return = lost_return*numpy.sqrt(trading_period)

            old_profile = statistics.calculate_moment_risk_return(ticker=ticker, sample_prices=previous_prices)
            old_var = old_profile['annual_volatility']**2
            old_mod_return = old_profile['annual_return']*numpy.sqrt(trading_period)

            new_actual_profile = statistics.calculate_moment_risk_return(ticker=ticker, sample_prices=new_prices)

            new_recursive_profile = {}
            new_recursive_profile['annual_return'] = estimators.recursive_rolling_mean(xbar_previous=old_profile['annual_return'],
                                                                                new_obs=new_return,
                                                                                lost_obs=lost_return)
            new_recursive_profile['annual_volatility'] = estimators.recursive_rolling_variance(var_previous=old_var,
                                                                                        xbar_previous=old_mod_return,
                                                                                        new_obs=new_mod_return,
                                                                                        lost_obs=lost_mod_return)
            new_recursive_profile['annual_volatility'] = numpy.sqrt(new_recursive_profile['annual_volatility'])
            # ito's lemma
            # new_recursive_profile['annual_return'] = new_recursive_profile['annual_return'] - 0.5 * (new_recursive_profile['annual_volatility'] ** 2)

            outputter.scalar_result(calculation=f'{ticker}_return({date})_actual', result=new_actual_profile['annual_return'],currency=False)
            outputter.scalar_result(calculation=f'{ticker}_return({date})_recursive', result=new_recursive_profile['annual_return'], currency=False)
            outputter.scalar_result(calculation=f'{ticker}_vol({date})_actual', result=new_actual_profile['annual_volatility'], currency=False)
            outputter.scalar_result(calculation=f'{ticker}_vol({date})_recursive', result=new_recursive_profile['annual_volatility'], currency=False)

# TODO: need to test service retrieval through command line to be confident it's returning the correct info.

if __name__ == "__main__":
    outputter.print_line()
    outputter.center('Percentile Testing')
    percentile_test()

    outputter.print_line()
    outputter.center("Regression Testing")
    outputter.print_line()
    outputter.title_line('Test Results')
    outputter.print_line()
    simple_regression_test()

    outputter.print_line()
    outputter.center("Rolling Sample Statistics Recursion Testing")
    outputter.print_line()
    outputter.title_line('Test Results')
    outputter.print_line()
    rolling_recursion_test()

    # outputter.print_line()
    # outputter.center('Rolling Recursive Risk Profile Test')
    # outputter.print_line()
    # outputter.title_line('Test Results')
    # outputter.print_line()
    # rolling_recursion_tests_with_financial_data()