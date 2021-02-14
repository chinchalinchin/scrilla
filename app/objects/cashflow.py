import datetime

import util.helper as helper

import app.settings as settings
import app.statistics as statistics
import app.services as services

FREQ_DAY=1/365
FREQ_MONTH=1/12
FREQ_QUARTER=1/4
FREQ_ANNUAL=1


class Cashflow:

    RISK_FREE_RATE = services.get_risk_free_rate()

    # NOTE: Growth function should be a function of time in years
    # NOTE: sample : { 'date_1' : 'value_1', 'date_2': 'value_2', ... }.
    # NOTE: sample must be ordered from latest to earliest, i.e. in descending order.
    def __init__(self, sample, frequency=FREQ_ANNUAL, growth_function=None):
        self.sample = sample
        self.frequency =frequency

        # If no sample provided, use simple linear regression
        if growth_function is None:
            self.generate_time_series_for_sample()
            self.regress_growth_function()

    def generate_time_series_for_sample(self):
        self.time_series = []

        dates, no_of_dates = self.sample.keys(), len(self.sample.keys())
        first_date = helper.parse_date_string(list(dates)[len(no_of_dates)])

        for date in dates:
            this_date = helper.parse_date_string(date)
            delta = (this_date - first_date).days
            time_in_years = delta / 365
            self.time_series.append(time_in_years)
    
    def regress_growth_function(self):
        self.beta = statistics.regression_beta(x=self.time_series, y=self.sample.items())
        self.alpha = statistics.regression_alpha(x=self.time_series, y=self.sample.items())
        

    def growth_function(self, x):
        if self.growth_function is None:
            return (alpha + beta*x)
        else: 
            return growth_function(x)

    # TODO: use trading days or actual days?
    def calculate_net_present_value(self, discount_rate=RISK_FREE_RATE):
        time_to_first_payment = 0
        if self.frequency == FREQ_ANNUAL:
            time_to_first_payment = helper.get_time_to_next_year()
            
        elif self.frequency == FREQ_QUARTER:
            time_to_first_payment = helper.get_time_to_next_quarter()

        elif self.frequency == FREQ_MONTH:
            time_to_first_payment = helper.get_time_to_next_month()

        elif self.frequency == FREQ_DAY:
            time_to_first_payment = FREQ_DAY

        self.NPV, i = 0, 0
        calculating = True
        while calculating: 
            previous_value = self.NPV
            current_time = time_to_first_payment + i * self.frequency
            self.NPV += growth_function(current_time) / (1 + discount_rate)**current_time

            if self.NPV - previous_value < settings.NPV_DELTA_TOLERANCE:
                calculating = False
            i += 1

        return self.NPV
            