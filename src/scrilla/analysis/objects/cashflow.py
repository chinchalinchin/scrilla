# This file is part of scrilla: https://github.com/chinchalinchin/scrilla.

# scrilla is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3
# as published by the Free Software Foundation.

# scrilla is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with scrilla.  If not, see <https://www.gnu.org/licenses/>
# or <https://github.com/chinchalinchin/scrilla/blob/develop/main/LICENSE>.

import datetime

from scrilla import services, settings, errors
from scrilla.static import constants
from scrilla.util import dater, outputter
import scrilla.analysis.estimators as estimators

logger = outputter.Logger(
    'scrilla.analysis.objects.cashflow', settings.LOG_LEVEL)

# Technically these are periods
FREQ_DAY = 1/365
FREQ_MONTH = 1/12
FREQ_QUARTER = 1/4
FREQ_ANNUAL = 1

# Frequency = 1 / period


class Cashflow:
    r"""
    A class that represents a set of future cashflows. The class is initialized with the `sample` variable, a `dict` of past cashflows and their dates. From the `sample`, a linear regression model is inferred. Alternatively, a `growth_function` can be provided that describes the cash flow as a function of time measured in years. If a `growth_function` is provided, the class skips the linear regression model. See warning below for more information on constructing an instance of this cashflow. In general, it needs to know how to project future cashflows, whether that is through inference or a model assumption. 

    If the sample of data is not large enough to infer a linear regression model, the estimation model will default to simple Martingale process described by the equation,

    $$ E(X_2 \mid X_1) = X_1 $$

    Or, in plain English, the next expected value given the current value is the current value. To rephrase it yet again: without more information the best guess for the future value of an asset is its current value.

    The growth model, whether estimated or provided, is used to project the future value of cashflows and then these projections are discounted back to the present by the `discount_rate`. 

    Parameters
    ----------
    1. **sample**: ``list``
        *Optional*. A list comprised of the cashflow\'s historical values. The list must be ordered from latest to earliest, i.e. in descending order. Must be of the format: `{ 'date_1' : 'value_1', 'date_2': 'value_2', ... }`
    2. **period**: ``float``
        *Optional*. The period between the cash flow payments. Measured as the length of time between two distinct cash flows, assuming all such payments are evenly spaced across time. The value should be measured in years. If a period is not specified, then a period will be inferred from the sample of data by averaging the time periods between successive payments in the sample. Common period are statically accessible through `FREQ_DAY`, `FREQ_MONTH`, `FREQ_QUARTER` and `FREQ_ANNUAL`. (*Yes, I know period = 1 / frequency; deal with it.*) 
    3. **growth_function**: ``function``
        *Optional*. A function that describes the cash flow as a function of time in years. If provided, the class will skip linear regression for estimating the cash flow model. If a `growth_function` is provided without a sample, a period must be specified. If a `growth_function` is provided with a sample and no period, the period will be inferred from the dates in the sample. If a `growth_function` is provided with a period, then the sample will be ignored altogether.
    4. **discount_rate**: ``float``
        *Optional.* The rate of return used to discount future cash flows back to the present. If not provided, the `discount_rate` defaults to the risk free rate defined by the **RISK_FREE** environment variable.
    5. **constant**: ``float``
        If the cashflow is constant with respect to time, specify the value of it with this argument. Will override `growth_function` and sample. If constant is specified, you MUST also specify a period or else you will encounter errors when trying to calculate the net present value of future cashflows.

    .. warning::
    * In general, the Cashflow object must always be initialized in one of the following ways:
        1. **__init__** args: (`sample`) -> period inferred from sample, linear regression used for growth
        2. **__init__** args: (`sample`, `period`) -> period from constructor, linear regression used for growth
        3. **__init__** args: (`sample`, `period`, `growth_function`) -> period from constructor, `growth_function` used for growth, sample ignored
        4. **__init__** args: (`sample`, `growth_function`) -> period inferred from sample, `growth_function` used for growth
        5. **__init__** args: (`period`, `growth_function`) -> period from constructor, `growth_function` used for growth
        6. **__init__** args: (`period`, `constant`) -> period from constructor, constant used for growth

    .. notes::
        * A constant cashflow can be specified in three ways: 1. By passing in a constant amount through the constructor `constant` variable. 2. By passing in a constant function with respect to time through the constructor `growth_function` variable. 3. By passing in a dataset of length one through the constructor `sample` variable.  In any of the cases, you MUST pass in a period or the `net_present_value` method of this class will return False.
        * Both a growth_function and a sample of data can be passed in at once to this class. If doing so, the `growth_function` will take precedence and be used for calculations in the `net_present_value` method. The sample will be used to infer the length of a period between cashflows, unless a period is also specified. If a period is specified in addition to `sample_prices` and `growth_function`, the period will take precedence over the period inferred from the sample of data.
        * The coefficients of the inferred linear regression are accessibly through `Cashflow().alpha` (intercept) and `Cashflow().beta` (slope) instance variables. The time series used to create the model is accessible through the `Cashflow().time_series` instance variable; Note: it is measured in years and the `start_date` is set equal to 0. In other words, the intercept of the model represents, approximately, the value of the cashflow on the `start_date`.

    .. todos::
        * Implement prediction interval function to get error bars for graphs and general usage.

    """

    def __init__(self, sample=None, period=None, growth_function=None, constant=None, discount_rate=None):
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
            logger.debug(
                'Cannot infer period from sample size less than or equal to 1')
            self.period = None
            self.frequency = None

        else:
            for date in dates:
                if first_pass:
                    tomorrows_date = dater.parse(date)
                    first_pass = False

                else:
                    todays_date = dater.parse(date)
                    delta = (tomorrows_date - todays_date).days / 365
                    mean_delta += delta / no_of_dates
                    tomorrows_date = todays_date

            self.period = mean_delta
            self.frequency = 1 / self.period
            logger.debug(f'Inferred period = {self.period} yrs')
            logger.debug(f'Inferred frequency = {self.frequency}')

    # TODO: trading days or actual days?
    def generate_time_series_for_sample(self):
        self.time_series = []

        dates, no_of_dates = self.sample.keys(), len(self.sample.keys())

        if no_of_dates == 0:
            logger.debug(
                'Cannot generate a time series for a sample size of 0.')
            self.time_series = None
        else:
            first_date = dater.parse(list(dates)[-1])

            for date in dates:
                this_date = dater.parse(date)
                delta = (this_date - first_date).days
                time_in_years = delta / 365
                self.time_series.append(time_in_years)

    # TODO: trading days or actual days?
    def calculate_time_to_today(self):
        first_date = dater.parse(list(self.sample.keys())[-1])
        today = datetime.date.today()
        return ((today - first_date).days/365)

    def regress_growth_function(self):
        to_list = [self.sample[date] for date in self.sample]

        self.beta = estimators.simple_regression_beta(
            x=self.time_series, y=to_list)
        self.alpha = estimators.simple_regression_alpha(
            x=self.time_series, y=to_list)

        if not self.beta or not self.alpha:
            if len(self.sample) > 0:
                self.alpha = list(self.sample.items())[0][1]
                logger.debug(
                    'Error calculating regression coefficients; Defaulting to Markovian process E(X2|X1) = X1.')
                logger.debug(f'Estimation model : y = {self.alpha}')
            else:
                raise errors.SampleSizeError(
                    'Not enough information to formulate estimation model.')

        else:
            logger.debug(
                f'Linear regression model : y = {self.beta} * x + {self.alpha}')

    def generate_model_series(self):
        return [self.alpha + self.beta*time for time in self.time_series]

    def generate_model_comparison(self):
        """
        Returns a list of dictionaries with the predicted value of the linear regression model and the actual value on a given datas. Format: [ {'date': `str`, 'model_price': `float`, 'actual_price': `float` }, ... ]
        """
        model_prices = self.generate_model_series()

        return[{'date': date,
                'model_price': model_prices[index],
                'actual_price': self.sample[date]}
               for index, date in enumerate(self.sample.keys())]

    def get_growth_function(self, x):
        """
        Traverses the hierarchy of instance variables to determine which method to use to describe the growth of future cashflows. Returns the value of determined function for the given value of `x`. Think of this function as a black box that hides the implementation of the `growth_function` from the user accessing the function. 

        Parameters
        ----------
        1. **x**: ``float``
            Time in years.

        Returns
        -------
        ``float`` : Value of the cash flow's growth function at time `x`.

        """
        if self.growth_function is None:
            if self.constant is not None:
                return self.constant
            return (self.alpha + self.beta*(x + self.time_to_today))
        return self.growth_function(x)

    # TODO: use trading days or actual days?
    def calculate_net_present_value(self):
        """
        Returns the net present value of the cash flow by using the `get_growth_function` method to project future cash flows and then discounting those projections back to the present by the value of the `discount_rate`. Call this method after constructing/initializing a `Cashflow` object to retrieve its NPV.

        Raises
        ------
        1. **scrilla.errors.InputValidationError**
            If not enough information is present in the instance of the `Cashflow` object to project future cash flows, this error will be thrown.

        Returns
        -------
        ``float`` : NPV of cash flow.
        """
        if self.period is None:
            raise errors.InputValidationError(
                "No period detected for cashflows. Not enough information to calculate net present value.")

        time_to_first_payment = 0
        if self.period is None:
            raise errors.InputValidationError(
                'Not enough information to calculate net present value of cash flow.')
        if self.period == FREQ_ANNUAL:
            time_to_first_payment = dater.get_time_to_next_year()

        elif self.period == FREQ_QUARTER:
            time_to_first_payment = dater.get_time_to_next_quarter()

        elif self.period == FREQ_MONTH:
            time_to_first_payment = dater.get_time_to_next_month()

        elif self.period == FREQ_DAY:
            time_to_first_payment = FREQ_DAY

        else:
            dates = self.sample.keys()
            latest_date = dater.parse(list(dates)[0])
            time_to_first_payment = dater.get_time_to_next_period(
                starting_date=latest_date, period=self.period)

        net_present_value, i, current_time = 0, 0, 0
        calculating = True
        while calculating:
            previous_value = net_present_value
            current_time = time_to_first_payment + i * self.period

            net_present_value += self.get_growth_function(current_time) / (
                (1 + self.discount_rate)**current_time)

            if net_present_value - previous_value < constants.constants['NPV_DELTA_TOLERANCE']:
                calculating = False
            i += 1

        return net_present_value
