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

from os import path
from sys import path as sys_path
from numpy import log, sqrt, exp
from scipy.stats import norm, multivariate_normal

if __name__=="__main__":
    APP_DIR = path.dirname(path.dirname(path.abspath(__file__)))
    sys_path.append(APP_DIR)

from scrilla import settings, errors, cache
import scrilla.util.outputter as outputter

logger = outputter.Logger('estimators', settings.LOG_LEVEL)
profile_cache = cache.ProfileCache()
correlation_cache = cache.CorrelationCache()

def univariate_normal_likelihood_function(params : list, data : list):
    """
    Description
    -----------
    This function returns the likelihood of a vector of parameters being observed from a sample univariate data of normal data. It is used as input in scipy.optimize. 

    Parameters
    ----------
    1. x : list
        Array representing a vector of parameters to be estimated, in this case the mean rate of return and volatility from a sample of data.
    2. data : list
        A list of data that has been drawn from a univariate normal population.
    """
    likelihood = 1
    for point in data:
        likelihood *= norm.pdf(x=point, loc=params[0], scale=params[1])
    return likelihood

def multivariate_likelihood_function(params: list, data: list):
    """
    Description
    -----------
    This function returns the likelihood of a vector of parameters being observed from a sample bivariate data of normal data. It is used as input in scipy.optimize. 

    Parameters
    ----------
    1. x : list \n
        Array representing a vector of parameters to be estimated, in this case the mean rate of return and volatility from a sample of data. \n\n
    2. data : list \n
        A list of data that has been drawn from a bivariate normal population. Must be formatted like,\n\t\t\t[ [x1,y1], [x2,y2],...]\n
    """
    likelihood = 1
    for point in data:
        likelihood *= multivariate_normal.pdf(x=point, mean=params[0], cov=params[1])
    return likelihood

def sample_percentile(data : list, percentile: float):
    """
    Description
    -----------
    Returns the observation in a sample data corresponding to the given percentile, i.e. the observation from a sorted sample where the percentage of the observations below that point is specified by the percentile. If the percentile falls between data points, the observation is smoothed based on the distance from the adjoining observations. 

    Parameters
    ----------
    1. data : list
        Array representing the set of data whose percentile is to be calculated.
    2. percentile: float
        The percentile corresponding to the desired observation.
    """
    data.sort()

    obs_number = (len(data) + 1)*percentile
    extrapolate = obs_number - int(obs_number)

    if extrapolate == 0:
        return data[int(obs_number)-1]
    elif obs_number > len(data):
        return data[-1]
    else:
        first_index = int(obs_number) - 1
        second_index = first_index + 1
        weight = obs_number - int(obs_number)
        return (1-weight)*data[first_index] + weight*data[second_index]

def sample_correlation(x : list, y: list):
    """
    
    Raises 
    ------
    1. scrilla.analysis.models.geometric.statistics.SampleSizeError \n \n

    Notes
    """
    if len(x) != len(y):
        raise errors.SampleSizeError('Samples are not of comparable lengths')

    if len(x) in [0, 1]:
        raise errors.SampleSizeError('Sample correlation cannot be computed for a sample size less than or equal to 1.')

    sumproduct, sum_x_squared, sum_x, sum_y, sum_y_squared= 0, 0, 0, 0, 0
    n = len(x)
    for i, item in enumerate(x):
        sumproduct += item*y[i]
        sum_x += item
        sum_x_squared += item**2
        sum_y += y[i]
        sum_y_squared += y[i]**2
    correl_num = ((n*sumproduct) - sum_x*sum_y)
    correl_den = sqrt((n*sum_x_squared-sum_x**2)*(n*sum_y_squared-sum_y**2))

    # LET'S DO SOME MATHEMATICS! (to get around division by zero!)
    #   Unfortunately, this only works when A and B > 0 because log
    #       of a negative number only exists in complex plane.
    #   1. correl = A/B
    #   2. log(correl) = log(A/B) = log(A) - log(B)
    #   3. exp(log(correl)) = exp(log(A/B))
    #   4. correl = exp(log(A/B))
    if correl_num > 0 and correl_den > 0:
        log_correl = log(correl_num) - log(correl_den)
        correlation = exp(log_correl)
    else:
        if correl_den != 0:
            correlation = correl_num / correl_den
        else:
            raise ValueError('Denominator for correlation formula to small for division')

    return correlation

def recursive_rolling_correlation(correl_previous, new_x_observation, lost_x_obs, 
                            new_y_obs, lost_y_obs, n=settings.DEFAULT_ANALYSIS_PERIOD):
    
    pass

def sample_mean(x: list):
    """
    
    Raises 
    ------
    1. scrilla.analysis.models.geometric.statistics.SampleSizeError \n \n
    """
    xbar, n = 0, len(x)

    if n == 0:
        raise errors.SampleSizeError('Sample mean cannot be computed for a sample size of 0.')

    for i in x:
        xbar += i/n
    return xbar

def recursive_rolling_mean(xbar_previous, new_obs, lost_obs, n=settings.DEFAULT_ANALYSIS_PERIOD):
    xbar_next = xbar_previous + (new_obs - lost_obs)/n
    return xbar_next

def sample_variance(x: list):
    """
    
    Raises 
    ------
    1. scrilla.analysis.models.geometric.statistics.SampleSizeError \n \n
    """

    try:
        mu, sigma, n = sample_mean(x=x), 0, len(x)
    except errors.SampleSizeError as e:
        raise errors.SampleSizeError(e)

    if n in [0, 1]:
        raise errors.SampleSizeError('Sample variance cannot be computed for a sample size less than or equal to 1.')

    for i in x:
        sigma += ((i-mu)**2)/(n-1)
    return sigma

def recursive_rolling_variance(var_previous, xbar_previous, new_obs, lost_obs, n=settings.DEFAULT_ANALYSIS_PERIOD):
    xbar_new = recursive_rolling_mean(xbar_previous=xbar_previous, new_obs=new_obs,
                                lost_obs=lost_obs, n=n)
    var_new = var_previous + (n/(n-1))*((new_obs**2 - lost_obs**2 )/n + (xbar_previous**2-xbar_new**2))
    return var_new

def sample_covariance(x: list, y: list):
    """
    
    Raises 
    ------
    1. scrilla.analysis.models.geometric.statistics.SampleSizeError \n \n
    """

    if len(x) != len(y):
        raise errors.SampleSizeError('Samples are not of comparable length')

    if len(x) in [0, 1]:
        raise errors.SampleSizeError('Sample correlation cannot be computed for a sample size less than or equal to 1.')

    # TODO: probably a faster way of calculating this.
    n, covariance = len(x), 0

    try:
        x_mean, y_mean = sample_mean(x=x), sample_mean(x=y)
    except errors.SampleSizeError as e:
        raise errors.SampleSizeError(e)

    for i, item in enumerate(x):
        covariance += (item - x_mean)*(y[i] - y_mean) / (n -1) 

    return covariance

def recursive_rolling_covariance(covar_previous, new_x_obs, lost_x_obs, previous_x_bar, 
                            new_y_obs, lost_y_obs, previous_y_bar, n=settings.DEFAULT_ANALYSIS_PERIOD):
    new_sum_term = new_x_obs*new_y_obs - lost_x_obs*lost_y_obs
    xy_cross_term = previous_x_bar*(new_y_obs-lost_y_obs)
    yx_cross_term = previous_y_bar*(new_x_obs-lost_x_obs)
    perturbation = (new_x_obs-lost_x_obs)*(new_y_obs-lost_y_obs) / n
    numerator = new_sum_term - xy_cross_term - yx_cross_term - perturbation    
    covar_new = covar_previous + numerator / (n-1)
    return covar_new

def simple_regression_beta(x: list, y: list):
    """
    
    Raises 
    ------
    1. scrilla.analysis.models.geometric.statistics.SampleSizeError \n \n
    """

    if len(x) != len(y):
        raise errors.SampleSizeError(f'len(x) = {len(x)} != len(y) = {len(y)}')
    if len(x) < 3:
        raise errors.SampleSizeError(f'Sample size of {len(x)} is less than the necessary degrees of freedom (n > 2) for regression estimation.')
    
    try:
        correl = sample_correlation(x=x, y=y)
        vol_x = sqrt(sample_variance(x=x))
        vol_y = sqrt(sample_variance(x=y))
    except errors.SampleSizeError as e:
        raise errors.SampleSizeError(e)

    beta = correl * vol_y / vol_x
    return beta

def simple_regression_alpha(x: list, y: list):
    """
    Raises 
    ------
    1. scrilla.analysis.models.geometric.statistics.SampleSizeError
    """

    if len(x) != len(y):
        raise errors.SampleSizeError(f'len(x) == {len(x)} != len(y) == {len(y)}')

    if len(x) < 3:
        raise errors.SampleSizeError(f'Sample size of {len(x)} is less than the necessary degrees of freedom (n > 2) for regression estimation.')
    
    try:
        y_mean, x_mean = sample_mean(y), sample_mean(x)
    except errors.SampleSizeError as e:
        raise errors.SampleSizeError(e)

    if not y_mean or not x_mean:
        logger.info('Error calculating statistics for regression alpha')
        return False
    
    alpha = y_mean - simple_regression_beta(x=x, y=y)*x_mean
    return alpha
    