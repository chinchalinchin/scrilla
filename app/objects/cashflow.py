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

    Parameters
    ----------
    sample: list { 'date_1' : 'value_1', 'date_2': 'value_2', ... } \n
        A list comprised of the cashflows historical values. The list must be ordered from latest to earliest, i.e. in descending order. \n \n
    period: float \n
        The period in years of the cash flow payments. Measure as the lenght of time between two distinct cash flows. The value should be measured in years. Common frequencies are statically accessible through FREQ_DAY, FREQ_MONTH, FREQ_QUARTER and FREQ_ANNUAL. \n \n 
    growth_function: function \n
        A function that describes the cash flow as a function of time in years. If provided, the class will skip linear regression for estimating the cash flow model. If providing a growth_function, specify sample = None in the arguments provided to the class constructor. \n \n
    """

    # NOTE: Growth function should be a function of time in years
    # NOTE: sample : { 'date_1' : 'value_1', 'date_2': 'value_2', ... }.
    # NOTE: sample must be ordered from latest to earliest, i.e. in descending order.
    def __init__(self, sample, period=None, growth_function=None):
        self.sample = sample
        self.period = period
        self.growth_function = growth_function

        # If no sample provided, use simple linear regression
        if growth_function is None:
            self.generate_time_series_for_sample()
            self.regress_growth_function()

        # If no frequency is specified, infer frequency from sample
        if period is None:
            self.infer_period()

    def infer_period(self):
        # no_of_dates = len - 1 because delta is being computed, i.e.
        #   lose one date.
        dates, no_of_dates = self.sample.keys(), (len(self.sample.keys()) -1 )
        first_pass = True
        mean_delta = 0

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
        
        output.debug(f'Linear regression model : y = {self.beta} * x + {self.alpha}')

    def get_growth_function(self, x):
        if self.growth_function is None:
            return (self.alpha + self.beta*x)
        else: 
            return self.growth_function(x)

    # TODO: use trading days or actual days?
    def calculate_net_present_value(self, discount_rate=None):
        if discount_rate is None:
            discount_rate = services.get_risk_free_rate()

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
            self.NPV += self.get_growth_function(current_time) / (1 + discount_rate)**current_time

            if self.NPV - previous_value < settings.NPV_DELTA_TOLERANCE:
                calculating = False
            i += 1

        return self.NPV
            