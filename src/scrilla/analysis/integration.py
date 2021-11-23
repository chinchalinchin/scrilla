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

"""
A module of functions for integrating stochastic differential equations through numerial techniques like Monte Carlo simulation.
"""
from typing import Callable
from scipy.stats import norm
from scipy.integrate import quad
from numpy import isinf, inf
import random

from scrilla import settings, errors
import scrilla.util.outputter as outputter

logger = outputter.Logger("scrilla.analysis.integration", settings.LOG_LEVEL)


def generate_random_walk(periods: int):
    return [norm.ppf(random.uniform(0, 1)) for i in range(periods)]

# Condition: E(integral of vol ^2 dt) < inf


def verify_volatility_condition(volatility_function: Callable) -> bool:
    r"""
    Ito calculus requires the class of volatility functions that scale a simple Weiner process (i.e., a process with independent, identically distributed increments with mean 0 and variance 1) satisfies the following

    $$ \int_{0}^{\infty} {\sigma (t)}^2 \,dt < \infty $$

    In order words, since the mean of an Weiner process increment is 0 (and thus \\(Var(X) = E(X^2)\\), this inequality imposes a condition on the process described by scaling the Weiner process by the volatility function: it must have a probability distribution that actually exists. This function returns a `bool` that signals whether or not the given function satisifies this condition.

    Parameters
    ----------
    1. **volatility_function** : ``Callable``
        A function that describes the volatility of a process as a function of time measured. Must accept scalar input.
    """
    integral = quad(func=lambda x: volatility_function(x)**2, a=0, b=inf)
    return not isinf(x=integral)

# Remember forward increments!


def ito_integral(mean_function: Callable, volatilty_function: Callable, upper_bound: float, iterations: int = 1000):
    r"""
    Approximates the expectation of an Ito integral from 0 to `upper_bound` for a Weiner process described by a mean and volatility that are functions of time, i.e.

    $$ E\{d X(t)\} = E \{ \int_{0}^{\infty} {\mu (t)} \, dt + \int_{0}^{\infty} {\sigma(t)} \, dW(t) \} $$

    Parameters
    ----------
    1. **mean_function** : ``Callable``
        A function that describes the mean of a process as a function of time. Must accept scalar input.
    2. **volatility_function** : ``Callable``
        A function that describes the volatility of a process as a function of time. Must accept scalar input.
    3. **upper_bound** : ``float``
        Upper limit for the integral.
    4. **iterations** : ``int``
        The number of iterations in the Reimann-Stieltjes sum.
    """
    if verify_volatility_condition(volatility_function=volatilty_function):
        # NOTE: Compute Ito Integral using forward increments due to the fact
        #       the value at the end of the interval can be conditioned on
        #       the value at the beginning of the interval. In other words, Ito
        #       Processes are Martingales, ie. E(X2 | X1) = X1.
        time_delta = upper_bound / settings.ITO_STEPS

        averaged_integral = 0
        for j in range(iterations):
            random_walk = generate_random_walk(settings.ITO_STEPS)
            this_integral, current_contribution = 0, 0
            current_contribution = 0
            for i in range(settings.ITO_STEPS):
                current_time = time_delta * i
                current_mean = mean_function(current_time)
                current_vol = volatilty_function(current_time)
                current_contribution = current_mean * \
                    time_delta + current_vol * random_walk[i]
                this_integral += current_contribution
            averaged_integral += this_integral/j

        return averaged_integral
    raise errors.UnboundedIntegral(
        'E(Integral(volatility_function^2 dt) from 0 to infinity < infinity)')
