import datetime

import util.helper as helper
import util.logger as logger

import app.settings as settings
import app.statistics as statistics
import app.services as services

output = logger.Logger('app.objects.cashflow', settings.LOG_LEVEL)

# Technically these are periods
FREQ_DAY=1/365
FREQ_MONTH=1/12
FREQ_QUARTER=1/4
FREQ_ANNUAL=1

# Frequency = 1 / period
class Cashflow:
    """
    Description
    -----------
    A class that represents a set of future cashflows. The class is initialized with a sample of past data and a linear regression model is inferred from the sample. Alternatively, a growth function can be provided that describes the cash flow as a function of time in years. If a growth function is provided, the class skips the linear regression model. \n \n

    If the sample of data is not large enough to infer a linear regression model, the estimation model will default to Markovian process where E(X2|X1) = X1, i.e. the next expected value given the current value is the current value, or put in plain english, without more information the best guess for the future value of an asset is its current value. \n \n

    The estimation model is used to project the future value of cashflows and then these projections are discounted back to the present by the risk free rate. A discount rate different from the risk free rate can be specified by providing the constructor a value for discount_rate. \n \n

    Parameters
    ----------
    sample: list { 'date_1' : 'value_1', 'date_2': 'value_2', ... } \n
        A list comprised of the cashflows historical values. The list must be ordered from latest to earliest, i.e. in descending order. \n \n
    period: float \n
        The period in years of the cash flow payments. Measure as the lenght of time between two distinct cash flows. The value should be measured in years. Common frequencies are statically accessible through FREQ_DAY, FREQ_MONTH, FREQ_QUARTER and FREQ_ANNUAL. \n \n 
    growth_function: function \n
        A function that describes the cash flow as a function of time in years. If provided, the class will skip linear regression for estimating the cash flow model. If providing a growth_function, specify sample = None in the arguments provided to the class constructor. \n \n
    discount_rate: float \n
        The rate of return used to discount future cash flows back to the present. If not provided, the discount_rate defaults to the risk free rate defined by the RISK_FREE environment variable. \n \n
    TODOs
    -----
    1. Implement prediction interval function to get error bars for graph.

    """

    # NOTE: Growth function should be a function of time in years
    # NOTE: sample : { 'date_1' : 'value_1', 'date_2': 'value_2', ... }.
    # NOTE: sample must be ordered from latest to earliest, i.e. in descending order.
    def __init__(self, sample, period=None, growth_function=None, discount_rate=None):
        self.sample = sample
        self.period = period
        self.growth_function = growth_function

        # If no sample provided, use simple linear regression
        if growth_function is None:
            self.generate_time_series_for_sample()
            self.regress_growth_function()
        
        if discount_rate is None:
            self.discount_rate = services.get_risk_free_rate()
        else:
            self.discount_rate = discount_rate

        output.debug(f'Using discount_rate = {self.discount_rate}')

        # If no frequency is specified, infer frequency from sample
        if period is None:
            self.infer_period()

    def infer_period(self):
        output.debug('Attempting to infer period/frequency of cashflows.')

        # no_of_dates = len - 1 because delta is being computed, i.e.
        #   lose one date.
        dates, no_of_dates = self.sample.keys(), (len(self.sample.keys()) - 1)
        first_pass = True
        mean_delta = 0

        if no_of_dates < 2:
            output.debug('Cannot infer period from sample size less than or equal to 1')
            self.period = None
            self.frequency = None

        else:
            for date in dates:
                if first_pass:
                    tomorrows_date = helper.parse_date_string(date)
                    first_pass = False

                else:
                    todays_date = helper.parse_date_string(date)
                    delta = (tomorrows_date - todays_date).days / 365
                    mean_delta += delta / no_of_dates 
                    tomorrows_date = todays_date

            self.period =  mean_delta
            self.frequency = 1 / self.period 
            output.debug(f'Inferred period = {self.period} yrs')
            output.debug(f'Inferred frequency = {self.frequency}')

    def generate_time_series_for_sample(self):
        self.time_series = []

        dates, no_of_dates = self.sample.keys(), len(self.sample.keys())

        if no_of_dates == 0:
            output.debug('Cannot generate a time series for a sample size of 0.')
        else:
            first_date = helper.parse_date_string(list(dates)[no_of_dates-1])

            for date in dates:
                this_date = helper.parse_date_string(date)
                delta = (this_date - first_date).days
                time_in_years = delta / 365
                self.time_series.append(time_in_years)
    
    def regress_growth_function(self):
        to_array = []
        for date in self.sample:
            to_array.append(self.sample[date])

        self.beta = statistics.regression_beta(x=self.time_series, y=to_array)
        self.alpha = statistics.regression_alpha(x=self.time_series, y=to_array)
        
        if not self.beta or not self.alpha:
            if len(self.sample) > 0:
                self.alpha = list(self.sample.items())[0][1]
                output.debug('Error calculating regression coefficients; Defaulting to Markovian process E(X2|X1) = X1.')
                output.debug(f'Estimation model : y = {self.alpha}')
            else: 
                output.debug('Not enough information to formulate estimation model.')
        else:
            output.debug(f'Linear regression model : y = {self.beta} * x + {self.alpha}')

    def get_growth_function(self, x):
        if self.growth_function is None:
            return (self.alpha + self.beta*x)
        else: 
            return self.growth_function(x)

    # TODO: use trading days or actual days?
    def calculate_net_present_value(self):
    
        if self.period is None:
            output.debug('No period detected for cashflows. Not enough information to calculate net present value.')
            return False
        else:

            time_to_first_payment = 0
            if self.period == FREQ_ANNUAL:
                time_to_first_payment = helper.get_time_to_next_year()
                
            elif self.period == FREQ_QUARTER:
                time_to_first_payment = helper.get_time_to_next_quarter()

            elif self.period == FREQ_MONTH:
                time_to_first_payment = helper.get_time_to_next_month()

            elif self.period == FREQ_DAY:
                time_to_first_payment = FREQ_DAY
            
            else:
                dates = self.sample.keys()
                latest_date = helper.parse_date_string(list(dates)[0])
                time_to_first_payment = helper.get_time_to_next_period(starting_date=latest_date, period=self.period)

            self.NPV, i = 0, 0
            calculating = True
            while calculating: 
                previous_value = self.NPV
                current_time = time_to_first_payment + i * self.period
                self.NPV += self.get_growth_function(current_time) / (1 + self.discount_rate)**current_time

                if self.NPV - previous_value < settings.NPV_DELTA_TOLERANCE:
                    calculating = False
                i += 1

            return self.NPV
            