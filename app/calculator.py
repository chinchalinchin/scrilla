
import scipy.stats as stats
import scipy.integrate as integrate
import numpy

import random

import app.settings as settings
import app.util.outputter as outputter

logger = outputter.Logger("app.calculator", settings.LOG_LEVEL)

def generate_random_walk(periods):
    return [stats.norm.ppf(random.uniform(0,1)) for i in range(periods)]

# Condition: E(integral of vol ^2 dt) < inf
def verify_volatility_condition(volatility_function):
    integral = integrate.quad(func=lambda x: volatility_function(x)**2, a=0, b=numpy.inf)
    return not numpy.isinf(x = integral)

# Remember forward increments!
def ito_integral(mean_function, volatilty_function, time_to_expiration=None):
    if verify_volatility_condition(volatility_function=volatilty_function):
        random_walk = generate_random_walk(settings.ITO_STEPS)
        
        # NOTE: Compute Ito Integral using forward increments due to the fact
        #       the value at the end of the interval can be conditioned on 
        #       the value at the beginning of the interval. In other words, Ito 
        #       Processes are Markovian, ie. E(X2 | X1) = X1.
        for i in range(settings.ITO_STEPS):
            # TODO
            pass
    else:
        logger.info('Supplied volatility function does not meet condition : ')
        logger.info('E(Integral(volatility_function^2 dt) from 0 to infinity < infinity)')