
import scipy.stats as stats
import scipy.integrate as integrate
import numpy

import random

import app.settings as settings
import util.logger as logger

output = logger.Logger("app.calculator", settings.LOG_LEVEL)

def generate_random_walk(periods):
    return [stats.norm.ppf(random.uniform(0,1)) for i in range(periods)]

# Condition: E(integral of vol ^2 dt) < inf
def verify_volatility_condition(volatility_function):
    squared_vol = lambda x: volatility_function(x)**2
    integral = integrate.quad(func=squared_vol, a=0, b=numpy.inf)
    return numpy.isinf(x = integral)

# NOTE: end_date
# Remember forward increments
def ito_integral(mean_function, volatilty_function, time_to_expiration=None):
    if verify_volatility_condition(volatility_function=volatilty_function):
        random_walk = generate_random_walk(settings.ITO_STEPS)
        
        for i in range(settings.ITO_STEPS):
            # compute ito integral
            pass
    else:
        output.debug('Supplied volatility function does not meet condition : ')
        output.debug('E(Integral(volatility_function^2 dt) from 0 to infinity)')