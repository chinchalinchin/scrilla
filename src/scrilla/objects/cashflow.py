import datetime
import util.helper as helper
import util.outputter as outputter

import services
import settings
import analysis.statistics as statistics

logger = outputter.Logger('objects.cashflow', settings.LOG_LEVEL)

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
    A class that represents a set of future cashflows. The class is initialized with the 'sample' variable, a list of past cashflows and their dates, and a linear regression model is inferred from the sample. Alternatively, a `growth_function` can be provided that describes the cash flow as a function of time in years. If a `growth_function` is provided, the class skips the linear regression model. \n \n

    If the sample of data is not large enough to infer a linear regression model, the estimation model will default to Markovian process where E(X2|X1) = X1, i.e. the next expected value given the current value is the current value, or put in plain english, without more information the best guess for the future value of an asset is its current value. \n \n

    The growth model, whether estimated or provided, is used to project the future value of cashflows and then these projections are discounted back to the present by the risk free rate. A discount rate different from the risk free rate can be specified by providing the constructor a value for discount_rate. \n \n

    Parameters
    ----------
    1. sample: list { 'date_1' : 'value_1', 'date_2': 'value_2', ... } \n
        A list comprised of the cashflow\'s historical values. The list must be ordered from latest to earliest, i.e. in descending order. \n \n
    2. period: float \n
        The period between the cash flow payments. Measured as the length of time between two distinct cash flows, assuming all such payments are evenly spaced across time. The value should be measured in years. If a period is not specified, then a period will be inferred from the sample of data by averaging the time periods between successive payments in the sample. Common period are statically accessible through `FREQ_DAY`, `FREQ_MONTH`, `FREQ_QUARTER` and `FREQ_ANNUAL`. (Yes, I know period = 1 / frequency; deal with it.) \n \n 
    3. growth_function: function \n
        A function that describes the cash flow as a function of time in years. If provided, the class will skip linear regression for estimating the cash flow model. If a `growth_function` is provided without a sample, a period must be specified. If a `growth_function` is provided with a sample and no period, the period will be inferred from the dates in the sample. If a `growth_function` is provided with a period, then the sample will be ignored altogether. \n \n
    4. discount_rate: float \n
        The rate of return used to discount future cash flows back to the present. If not provided, the `discount_rate` defaults to the risk free rate defined by the **RISK_FREE** environment variable. \n \n
    5. constant: float \n
        If the cashflow is constant with respect to time, specify the value of it with this argument. Will override `growth_function` and sample. If constant is specified, you MUST also specify a period or else you will encounter errors when trying to calculate the net present value of future cashflows. \n \n
    
    NOTES
    -----
    NOTE #1: A constant cashflow can be specified in three ways: 1. By passing in a constant amount through the constructor `constant` variable. 2. By passing in a constant function with respect to time through the constructor `growth_function` variable. 3. By passing in a dataset of length one through the constructor `sample` variable.  In any of the cases, you MUST pass in a period or the `net_present_value` method of this class will return False. \n \n

    NOTE #2: Both a growth_function and a sample of data can be passed in at once to this class. If doing so, the `growth_function` will take precedence and be used for calculations in the `net_present_value` method. The sample will be used to infer the length of a period between cashflows, unless a period is also specified. If a period is specified in addition to sample and `growth_function`, the period will take precedence over the period inferred from the sample of data. \n \n

    NOTE #3: In general, the Cashflow object must always be initialized in one of the following ways: \n
        1. Constructor args: (`sample`) -> period inferred from sample, linear regression used for growth
        2. Constructor args: (`sample`, `period`) -> period from constructor, linear regression used for growth
        3. Constructor args: (`sample`, `period`, `growth_function`) -> period from constructor, `growth_function` used for growth, sample ignored
        4. Constructor args: (`sample`, `growth_function`) -> period inferred from sample, `growth_function` used for growth
        5. Constructor args: (`period`, `growth_function`) -> period from constructor, `growth_function` used for growth
        6. Constructor args: (`period`, `constant`) -> period from constructor, constant used for growth
    TODOs
    -----
    1. Implement prediction interval function to get error bars for graphs and general usage.

    """
    def __init__(self, sample=None, period=None, growth_function=None, discount_rate=None, constant=None):
        self.sample = sample
        self.period = period
        self.growth_function = growth_function

        # if constant is specified, override sample and growth_function
        if constant is not None:
            logger.debug(f'constant = $ {constant}; period MUST NOT be null!')
            logger.debug(f'period = {self.period}')
            self.constant = constant
            self.sample = None
            self.growth_function = None
        else:
            self.constant = None

        # If sample provided, use simple linear regression
        if self.sample is not None and self.growth_function is None:
            self.generate_time_series_for_sample()
            self.regress_growth_function()
        
        if discount_rate is None:
            self.discount_rate = services.get_risk_free_rate()
        else:
            self.discount_rate = discount_rate

        logger.debug(f'Using discount_rate = {self.discount_rate}')

        # If no frequency is specified, infer frequency from sample
        if self.sample is not None and self.period is None:
            self.infer_period()

        if self.sample is not None and len(self.sample) > 0:
            self.time_to_today = self.calculate_time_to_today()

    def infer_period(self):
        logger.debug('Attempting to infer period/frequency of cashflows.')

        # no_of_dates = len - 1 because delta is being computed, i.e.
        #   lose one date.
        dates, no_of_dates = self.sample.keys(), (len(self.sample.keys()) - 1)
        first_pass = True
        mean_delta = 0

        if no_of_dates < 2:
            logger.debug('Cannot infer period from sample size less than or equal to 1')
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
            logger.debug(f'Inferred period = {self.period} yrs')
            logger.debug(f'Inferred frequency = {self.frequency}')

    def generate_time_series_for_sample(self):
        self.time_series = []

        dates, no_of_dates = self.sample.keys(), len(self.sample.keys())

        if no_of_dates == 0:
            logger.debug('Cannot generate a time series for a sample size of 0.')
            self.time_series = None
        else:
            first_date = helper.parse_date_string(list(dates)[-1])

            for date in dates:
                this_date = helper.parse_date_string(date)
                delta = (this_date - first_date).days
                time_in_years = delta / 365
                self.time_series.append(time_in_years)
    
    def calculate_time_to_today(self):
        first_date = helper.parse_date_string(list(self.sample.keys())[-1])
        today = datetime.date.today()
        return ((today - first_date).days/365)
        

    def regress_growth_function(self):
        to_array = []
        for date in self.sample:
            to_array.append(self.sample[date])

        self.beta = statistics.regression_beta(x=self.time_series, y=to_array)
        self.alpha = statistics.regression_alpha(x=self.time_series, y=to_array)
        
        if not self.beta or not self.alpha:
            if len(self.sample) > 0:
                self.alpha = list(self.sample.items())[0][1]
                logger.debug('Error calculating regression coefficients; Defaulting to Markovian process E(X2|X1) = X1.')
                logger.debug(f'Estimation model : y = {self.alpha}')
            else: 
                logger.debug('Not enough information to formulate estimation model.')
        else:
            logger.debug(f'Linear regression model : y = {self.beta} * x + {self.alpha}')

    def get_growth_function(self, x):
        if self.growth_function is None:
            if self.constant is not None:
                return self.constant
            return (self.alpha + self.beta*(x + self.time_to_today))
        return self.growth_function(x)

    # TODO: use trading days or actual days?
    def calculate_net_present_value(self):
    
        if self.period is None:
            logger.debug('No period detected for cashflows. Not enough information to calculate net present value.')
            return False
        
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

        self.NPV, i, current_time = 0, 0, 0
        calculating = True
        while calculating: 
            previous_value = self.NPV

            if self.period is not None:
                current_time = time_to_first_payment + i * self.period
            else:
                logger.debug('Not enough information to calculate net present value of cash flow.')
                return False
            
            self.NPV += self.get_growth_function(current_time) / ((1 + self.discount_rate)**current_time)

            if self.NPV - previous_value < settings.NPV_DELTA_TOLERANCE:
                calculating = False
            i += 1

        return self.NPV
        