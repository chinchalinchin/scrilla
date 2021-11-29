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
This module contains probability functions unique to the Geometric Brownian Motion stochastic model. All functions assume an asset price process that follows GBM. In other words, the return distribution is lognormal. This is equivalent to the Black-Scholes model from finance. 

The calculations have no stance on whether the actual probability distribution or the risk-neutral probability distribution should be used. This is implicitly specified by the user when they provided a rate of return to functions in this module. If the user wishes to use a risk-neutral probability, simply provide the assumed risk-free rate. If the user wishes to use an actual probability, provide the estimate of the rate of the return for the asset.
"""
from scipy.stats import norm
from math import sqrt, exp, log
from scrilla import settings
from scrilla.util.outputter import Logger

logger = Logger('scrilla.analysis.models.geometric.statistics',
                settings.LOG_LEVEL)


def d1(S0: float, ST: float, vol: float, ret: float, expiry: float, div: float = 0) -> float:
    """
    Returns the value of *d1* defined by the Black Scholes model (Geometric Brownian Motion)

    Parameters
    ----------
    1. **S0** : ``float`
        Initial value of the asset.
    2. **ST** : ``float``
        Final value of the asset.
    3. **vol**: ``float``
        Annualized volatility of the asset price process.
    4. **ret**: ``float``
        Annualized return of the asset price process.
    5. **expiry**: ``float``
        Time horizon in years, i.e. the time delta between `ST` and `S0` measured in years. 
    6. **div**: ``float``
        *Optional*. Annualized dividend yield. Defaults to 0.

    Returns
    -------
    ``float`` : Black-Scholes *d1*
    """
    numerator = log(S0/ST) + (ret - div + 0.5 * (vol ** 2))*expiry
    denominator = vol * sqrt(expiry)
    return (numerator/denominator)


def d2(S0: float, ST: float, vol: float, ret: float, expiry: float, div: float = 0) -> float:
    """
    Returns the value of *d2* defined by the Black Scholes model (Geometric Brownian Motion)

    Parameters
    ----------
    1. **S0** : ``float``
        Initial value of the asset.
    2. **ST** : ``float``
        Final value of the asset.
    3. **vol**: ``float``
        Annualized volatility of the asset price process.
    4. **ret**: ``float``
        Annualized return of the asset price process.
    5. **expiry**: ``float``
        Time horizon in years, i.e. the time delta between `ST` and `S0` measured in years. 
    6. **div**: ``float``
        *Optional*. Annualized dividend yield. Defaults to 0.

    Returns
    -------
    ``float`` : Black-Scholes *d2*
    """
    thisD1 = d1(S0=S0, ST=ST, vol=vol, ret=ret, expiry=expiry, div=div)
    adjust = vol * sqrt(expiry)
    return (thisD1 - adjust)


def prob_d1(S0: float, ST: float, vol: float, ret: float, expiry: float, div: float = 0, neg: bool = False) -> float:
    """
    Returns the probability of *d1* defined by the Black Scholes model (Geometric Brownian Motion)

    Parameters
    ----------
    1. **S0** : ``float``
        Initial value of the asset.
    2. **ST** : ``float`
        Final value of the asset.
    3. **vol**: ``float``
        Annualized volatility of the asset price process.
    4. **ret**: ``float``
        Annualized return of the asset price process.
    5. **expiry**: ``float``
        Time horizon in years, i.e. the time delta between `ST` and `S0` measured in years. 
    6. **div**: ``float``
        *Optional*. Annualized dividend yield. Defaults to 0.  
    7. **neg**: ``bool``
        *Optional*. Calculates the probability of *-d1*. Defaults to `False`.

    Returns
    -------
    ``float`` : cumulative probability of *d1*
    """
    if vol == 0:
        pass
    thisD1 = d1(S0=S0, ST=ST, vol=vol, ret=ret, expiry=expiry, div=div)
    if neg:
        thisD1 = -thisD1
    return norm.cdf(thisD1)


def prob_d2(S0: float, ST: float, vol: float, ret: float, expiry: float, div: float = 0, neg: bool = False):
    """
    Returns the probability of *d2* defined by the Black Scholes model (Geometric Brownian Motion)

    Parameters
    ----------
    1. **S0** : ``float``
        Initial value of the asset.
    2. **ST** : ``float`
        Final value of the asset.
    3. **vol**: ``float``
        Annualized volatility of the asset price process.
    4. **ret**: ``float``
        Annualized return of the asset price process.
    5. **expiry**: ``float``
        Time horizon in years, i.e. the time delta between `ST` and `S0`. 
    6. **div**: ``float``
        *Optional*. Annualized dividend yield. Defaults to 0.  
    7. **neg**: ``bool``
        *Optional*. Calculates the probability of *-d2*. Defaults to `False`.

    Returns
    -------
    ``float`` : cumulative probability of *d2*
    """
    # if no uncertainty
    if vol == 0:
        # if the future value of initial price is greater than the strike
        if S0*exp((ret-div)*expiry) > ST:
            # probability(S>St)=1
            return 1
        # probability(S>St)=0
        return 0

    thisD2 = d2(S0=S0, ST=ST, vol=vol, ret=ret, expiry=expiry, div=div)
    if neg:
        thisD2 = -thisD2
    return norm.cdf(thisD2)


def percentile(S0: float, vol: float, ret: float, expiry: float, prob: float, div: float = 0) -> float:
    """
    Returns the final value of the asset price over the time horizon `expiry` that corresponds the `percentile` of the price's distribution. The asset price process is assumed to follow Geometric Brownian Motion, i.e. the return distribution is lognormal. 

    Parameters
    ----------
    1. **S0** : ``float``
        Initial value of the asset.
    2. **vol**: ``float``
        Annualized volatility of the asset price process.
    3. **ret**: ``float``
        Annualized return of the asset price process.
    4. **expiry**: ``float``
        Time horizon in years, i.e. the time delta between `ST` and `S0` measured in years. 
    5. **prob**: ``float``
        Percentile of the distribution to be returned, i.e. if S is the price process and \\(S_t\\) is the percentile,

        $$ Pr(S<S_t)=prob $$

    6. **div**: ``float``
        *Optional*. Annualized dividend yield. Defaults to 0. 

    Returns
    -------
    ``float`` : percentile of lognormal distribution

    .. notes::
        * Percentiles are preserved under log transformations, so the asset percentile is equal to the exponentiated return percentile. See Wiki article for more information: https://en.wikipedia.org/wiki/Log-normal_distribution#Mode,_median,_quantiles
    """
    inv_norm = norm.ppf(prob)
    exponent = (ret - div - 0.5*(vol**2))*expiry + vol*sqrt(expiry)*inv_norm
    return (S0*exp(exponent))


def conditional_expected_value(S0: float, vol: float, ret: float, expiry: float, conditional_value: float,  greater: bool = False, div: float = 0) -> float:
    """
    Calculates the conditional expected value of an equity, assuming the price process follows Geometric Brownian Motion, i.e. the price distribution is lognormal.

    Note: Returns either
        >>> if greater:
            >>> E( St | St > condtional_value)
        >>> if not greater:
            >>> E( St | St < conditional_value)

    Parameters
    ----------
    1. **S0** : ``float``
        Initial equity price.
    2. **vol** : ``float``
        Annualized volatility.
    3. ***ret**: ``float``
        Annualized return.
    4. **expiry** : ``float``
        Time in years until the condition is evaluated.
    5. **conditional_value**: ``float``
        The value of the equity conditioned on at time ``expiry``.
    6. **greater** : ``boolean``
        *Optional*. Defaults to `False`. Determines the direction of the inequality for the condition attached to the expectation. See function description for more information.
    7. **div**: ``float``
        *Optional*. Defaults to `0`. Annualized dividend yield.
    """
    forward_value = S0*exp((ret - div)*expiry)
    if greater:
        this_prob_d1 = prob_d1(S0=S0, ST=conditional_value,
                               vol=vol, ret=ret, expiry=expiry, div=div)
        this_prob_d2 = prob_d2(S0=S0, ST=conditional_value,
                               vol=vol, ret=ret, expiry=expiry, div=div)
    else:
        this_prob_d1 = prob_d1(S0=S0, ST=conditional_value,
                               vol=vol, ret=ret, expiry=expiry, div=div, neg=True)
        this_prob_d2 = prob_d2(S0=S0, ST=conditional_value,
                               vol=vol, ret=ret, expiry=expiry, div=div, neg=True)

    return (forward_value*this_prob_d1/this_prob_d2)
