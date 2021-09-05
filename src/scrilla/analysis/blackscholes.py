from scipy.stats import norm
from numpy import log, sqrt, exp

def d1(S0, ST, vol, ret, expiry, div = 0):
    numerator = log(S0/ST) + (ret - div + 0.5 * (vol **2))*expiry
    denominator = vol * sqrt(expiry)
    return (numerator/denominator)

def d2(S0, ST, vol, ret, expiry, div = 0):
    thisD1 = d1(S0=S0, ST=ST, vol=vol, ret=ret, expiry=expiry, div=div)
    adjust = vol * sqrt(expiry)
    return (thisD1 - adjust)

def prob_d1(S0, ST, vol, ret, expiry, div=0, neg=False):
    thisD1 = d1(S0=S0, ST=ST, vol=vol, ret=ret, expiry=expiry, div=div)
    if neg:
        thisD1 = -thisD1
    return norm.cdf(thisD1)


def prob_d2(S0, ST, vol, ret, expiry, div=0, neg=False):
    thisD2 = d2(S0=S0, ST=ST, vol=vol, ret=ret, expiry=expiry, div=div)
    if neg:
        thisD2 = -thisD2
    return norm.cdf(thisD2)

def percentile(S0, vol, ret, expiry, percentile, div=0):
    inv_norm = norm.ppf(percentile)
    exponent = (ret - div - 0.5*(vol**2))*expiry + vol*sqrt(expiry)*inv_norm
    return (S0*exp(exponent))

def conditional_expected_value(S0, vol, ret, expiry, conditional_value,  greater = False, div=0,):
    """
    Description
    -----------
    Calculates the conditional expected value of an equity as described the Black Scholes model.\n \n
    
    Note: Returns either, \n
        if greater: \n
            E( St | St > condtional_value) \n
        if not greater:
            E( St | St < conditional_value) \n \n
    
    Parameters
    ----------
    1. S0 : float \n
        Initial equity price. \n
    2. vol : float \n
        Annualized volatility. \n
    3. ret: float \n
        Annualized return. \n
    4. expiry : float \n 
        Time in years. \n
    5. conditional_value: float \n
        The value of the equity conditioned on at time 'expiry' \n
    6. greater : boolean \n
        Defaults to `False`. Determines the direction of the inequality as the condition for the expectation. See Description for more information. \n
    7. div : float \n
        Defaults to `0`. Annualized dividend yield. 
    Notes
    -----
    1. Important! This is not the risk-neutral conditional expected value; it is the conditional expected value as determined by the stochastic process describing the equity's actual probability distribution.
    """
    forward_value = S0*exp( (ret - div)*expiry)
    if greater:
        this_prob_d1 = prob_d1(S0=S0, ST=conditional_value, vol=vol, ret=ret, expiry=expiry, div=div)
        this_prob_d2 = prob_d2(S0=S0, ST=conditional_value, vol=vol, ret=ret, expiry=expiry, div=div)
    else:
        this_prob_d1 = prob_d1(S0=S0, ST=conditional_value, vol=vol, ret=ret, expiry=expiry, div=div, neg=True)
        this_prob_d2 = prob_d2(S0=S0, ST=conditional_value, vol=vol, ret=ret, expiry=expiry, div=div, neg=True)

    return (forward_value*this_prob_d1/this_prob_d2)