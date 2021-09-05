from scipy.stats import norm
from numpy import log, sqrt, exp

def bs_conditional_expected_value(S0, vol, ret, expiry, conditional_value,  greater = True, div=0,):
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
        Defaults to `True`. Determines the direction of the inequality as the condition for the expectation. See Description for more information. \n
    7. div : float \n
        Defaults to `0`. Annualized dividend yield. 
    Notes
    -----
    1. Important! This is not the risk-neutral conditional expected value; it is the conditional expected value as determined by the stochastic process describing the equity's actual probability distribution.
    """
    forward_value = S0*exp( (ret - div)*expiry)
    if greater:
        prob_d1 = bs_prob_d1(S0=S0, ST=conditional_value, vol=vol, ret=ret, expiry=expiry, div=div)
        prob_d2 = bs_prob_d2(S0=S0, ST=conditional_value, vol=vol, ret=ret, expiry=expiry, div=div)
    else:
        prob_d1 = bs_prob_d1(S0=S0, ST=conditional_value, vol=vol, ret=ret, expiry=expiry, div=div, neg=True)
        prob_d2 = bs_prob_d2(S0=S0, ST=conditional_value, vol=vol, ret=ret, expiry=expiry, div=div, neg=True)

    return (forward_value*prob_d1/prob_d2)

def bs_d1(S0, ST, vol, ret, expiry, div = 0):
    numerator = log(S0/ST) + (ret - div + 0.5 * (vol **2))*expiry
    denominator = vol * sqrt(expiry)
    return (numerator/denominator)

def bs_d2(S0, ST, vol, ret, expiry, div = 0):
    d1 = bs_d1(S0=S0, ST=ST, vol=vol, ret=ret, expiry=expiry, div=div)
    adjust = vol * sqrt(expiry)
    return (d1 - adjust)

def bs_prob_d1(S0, ST, vol, ret, expiry, div=0, neg=False):
    d1 = bs_d1(S0=S0, ST=ST, vol=vol, ret=ret, expiry=expiry, div=div)
    if neg:
        d1 = -d1
    return norm.cdf(d1)


def bs_prob_d2(S0, ST, vol, ret, expiry, div=0, neg=False):
    d2 = bs_d2(S0=S0, ST=ST, vol=vol, ret=ret, expiry=expiry, div=div)
    if neg:
        d2 = -d2
    return norm.cdf(d2)