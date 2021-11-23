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
A module of statistical point estimators and likelihood functions.
"""

from os import path
from sys import path as sys_path
from typing import List
from numpy import log, sqrt, exp, inf
from scipy.stats import norm, multivariate_normal

if __name__ == "__main__":
    APP_DIR = path.dirname(path.dirname(path.abspath(__file__)))
    sys_path.append(APP_DIR)

from scrilla import settings, errors, cache
import scrilla.util.outputter as outputter

logger = outputter.Logger('scrilla.analysis.estimators', settings.LOG_LEVEL)
profile_cache = cache.ProfileCache()
correlation_cache = cache.CorrelationCache()


def univariate_normal_likelihood_function(params: list, data: list) -> float:
    """
    This function returns the likelihood of a vector of parameters being observed from a sample univariate data of normal data. It can be used as objective function input for `scipy.optimize`'s optimization methods. 

    Parameters
    ----------
    1. **x** : ``list``
        Array representing a vector of parameters , in this case the mean rate of return and volatility from a sample of data.
    2. **data** : ``list``
        A list of data that has been drawn from a univariate normal population.
    """
    likelihood = 0
    for point in data:
        likelihood += norm.logpdf(x=point, loc=params[0], scale=params[1])
    return likelihood


def bivariate_normal_likelihood_function(params: list, data: list) -> float:
    r"""
    Returns the likelihood of a vector of parameters being observed from a sample bivariate data of normal data. It can be used as objective function input for `scipy.optimize`'s optimization methods. 

    Parameters
    ----------
    1. **params** : ``list``
        Array representing a vector of parameters, in this case the mean rate of returns, voledatilities and covariance for a bivariate normal distribution. *Important*: The vector must be order: 1. params[0] = \\(\mu_x\\), params[1]=\\(\mu_y\\), params[2] = \\(\sigma_x\\), params[3] = \\(\sigma_y\\), params[4] = \\(\rho_{xy} \cdot \sigma_x \cdot \sigma_y\\). The matrix is parameterized in this manner in order to interface more easily with `scipy.optimize.minimize`.
    2. **data** : ``list``
        A list of data that has been drawn from a bivariate normal population. Must be formatted in the following manner: `[ [x1,y1], [x2,y2],...]`

    .. notes::
        * the covariance matrix of a bivariate normal distribution must be positive semi-definite (PSD) and non-singular. PSD can be checked with the [Slyvester Criterion](https://en.wikipedia.org/wiki/Sylvester%27s_criterion) or [Cauchy-Schwarz Inequality](https://en.wikipedia.org/wiki/Cauchy%E2%80%93Schwarz_inequality#Probability_theory). Since sample variance will always be positive, this reduces to checking the determinant of the covariance matrix is greater than 0. This function will return `numpy.inf` if the covariance matrix is singular or non-positive semi-definite.

    """
    mean = [params[0], params[1]]
    cov = [[params[2], params[4]], [params[4], params[3]]]

    determinant = params[2]*params[3] - params[4]**2
    if determinant == 0 or determinant < 0 or determinant < 0.00000001:
        return inf

    likelihood = 0
    for point in data:
        likelihood += multivariate_normal.logpdf(x=point, mean=mean, cov=cov)
    return likelihood


def sample_percentile(data: list, percentile: float):
    """
    Returns the observation in a sample data corresponding to the given percentile, i.e. the observation from a sorted sample where the percentage of the observations below that point is specified by the percentile. If the percentile falls between data points, the observation is smoothed based on the distance from the adjoining observations in the following manner,

    .. todo:: add latex here

    Parameters
    ----------
    1. **data** : ``list``
        Array representing the set of data whose percentile is to be calculated.
    2. **percentile**: ``float``
        The percentile corresponding to the desired observation.
    """
    data.sort()

    obs_number = (len(data) + 1)*percentile
    extrapolate = obs_number - int(obs_number)

    if extrapolate == 0:
        return data[int(obs_number)-1]
    if obs_number > len(data):
        return data[-1]
    first_index = int(obs_number) - 1
    second_index = first_index + 1
    weight = obs_number - int(obs_number)
    return (1-weight)*data[first_index] + weight*data[second_index]


def sample_correlation(x: list, y: list):
    """
    Returns the sample correlation calculated using the Pearson correlation coefficient estimator,

    .. todo:: Pearson coefficient formula here

    Parameters
    ----------
    1. **x**: ``list``
        The *x* sample of paired data (*x*, *y*). Must preserve order with **y**.
    2. **y**: ``list``
        The *y* sample of paired data (*x*, *y*). Must preserve order with **x**.

    Raises 
    ------
    1. `scrilla.errors.SampleSizeError` :
        If the sample sizes do not meet the requirements for estimation, this error will be thrown.
    2. **ValueError** :
        If the denominator of the correlation coefficient becomes too small for floating point arithmetic, this error is thrown.

    .. todos ::
        * Possibly wrap the correlation coefficient numerator and denominator in `Decimal` class before calculation to bypass the **ValueError** that occurs in some samples where the denominator is too small for the arithmetic to detect.
    """
    if len(x) != len(y):
        raise errors.SampleSizeError('Samples are not of comparable lengths')

    if len(x) in [0, 1]:
        raise errors.SampleSizeError(
            'Sample correlation cannot be computed for a sample size less than or equal to 1.')

    sumproduct, sum_x_squared, sum_x, sum_y, sum_y_squared = 0, 0, 0, 0, 0
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
            raise ValueError(
                'Denominator for correlation formula to small for division')

    return correlation


def recursive_rolling_correlation(correl_previous, new_x_observation, lost_x_obs,
                                  new_y_obs, lost_y_obs, n=settings.DEFAULT_ANALYSIS_PERIOD):

    pass


def sample_mean(x: list) -> float:
    r"""
    Returns the sample mean from a sample of data \\(\{x_1 , x_2, ... , x_n \}\\),

    $$ \bar{x} = \frac{\sum_{i=1}^{n} x_i}/{n} $$

    Parameters
    ----------
    1. **x**: ``list``
        List containing a sample of numerical data.

    Raises 
    ------
    1. `scrilla.errors.SampleSizeError`
        If ``len(x)==0``, this error will be thrown.
    """
    xbar, n = 0, len(x)

    if n == 0:
        raise errors.SampleSizeError(
            'Sample mean cannot be computed for a sample size of 0.')

    for i in x:
        xbar += i/n
    return xbar


def recursive_rolling_mean(xbar_previous, new_obs, lost_obs, n=settings.DEFAULT_ANALYSIS_PERIOD):
    xbar_next = xbar_previous + (new_obs - lost_obs)/n
    return xbar_next


def sample_variance(x: list):
    r"""
    Returns the sample variance from a sample of data \\(\{x_1 , x_2, ... , x_n \}\\),

    $$ s^2=\frac{\sum_{i=1}^{n} (x_i - \bar{x})^2}/{n-1} $$

    Parameters
    ----------
    1. **x**: ``list``
        List containing a sample of numerical data.

    Raises 
    ------
    1. `scrilla.errors.SampleSizeError`
    """

    mu, sigma, n = sample_mean(x=x), 0, len(x)

    if n in [0, 1]:
        raise errors.SampleSizeError(
            'Sample variance cannot be computed for a sample size less than or equal to 1.')

    for i in x:
        sigma += ((i-mu)**2)/(n-1)
    return sigma


def recursive_rolling_variance(var_previous, xbar_previous, new_obs, lost_obs, n=settings.DEFAULT_ANALYSIS_PERIOD):
    xbar_new = recursive_rolling_mean(xbar_previous=xbar_previous, new_obs=new_obs,
                                      lost_obs=lost_obs, n=n)
    var_new = var_previous + \
        (n/(n-1))*((new_obs**2 - lost_obs**2)/n + (xbar_previous**2-xbar_new**2))
    return var_new


def sample_covariance(x: list, y: list):
    """
    Parameters
    ----------
    1. **x**: ``list``
        The *x* sample of paired data (*x*, *y*). Must preserve order with **y**.
    2. **y**: ``list``
        The *y* sample of paired data (*x*, *y*). Must preserve order with **x**.

    Raises 
    ------
    1. `scrilla.errors.SampleSizeError`
        If ``len(x) != len(y)`` (samples of incomparable length) or ``len(x) in [0,1]`` (insufficient data/degrees of freedom), this error will be thrown.
    """

    if len(x) != len(y):
        raise errors.SampleSizeError('Samples are not of comparable length')

    if len(x) in [0, 1]:
        raise errors.SampleSizeError(
            'Sample correlation cannot be computed for a sample size less than or equal to 1.')

    n, covariance = len(x), 0

    x_mean, y_mean = sample_mean(x=x), sample_mean(x=y)

    for i, item in enumerate(x):
        covariance += (item - x_mean)*(y[i] - y_mean) / (n - 1)

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
    Parameters
    ----------
    1. **x**: ``list``
        The *x* sample of paired data (*x*, *y*). Must preserve order with **y**.
    2. **y**: ``list``
        The *y* sample of paired data (*x*, *y*). Must preserve order with **x**.

    Raises 
    ------
    1. `scrilla.errors.statistics.SampleSizeError`
        If ``len(x) != len(y)`` (samples of incomparable length) or ``len(x) < 3`` (insufficient data/degrees of freedom), this error will be thrown.
    """

    if len(x) != len(y):
        raise errors.SampleSizeError(f'len(x) = {len(x)} != len(y) = {len(y)}')
    if len(x) < 3:
        raise errors.SampleSizeError(
            f'Sample size of {len(x)} is less than the necessary degrees of freedom (n > 2) for regression estimation.')

    correl = sample_correlation(x=x, y=y)
    vol_x = sqrt(sample_variance(x=x))
    vol_y = sqrt(sample_variance(x=y))

    beta = correl * vol_y / vol_x
    return beta


def simple_regression_alpha(x: list, y: list):
    """
    Parameters
    ----------
    1. **x**: ``list``
        The *x* sample of paired data (*x*, *y*). Must preserve order with **y**.
    2. **y**: ``list``
        The *y* sample of paired data (*x*, *y*). Must preserve order with **x**.

    Raises 
    ------
    1. `scrilla.errors.SampleSizeError`
        If ``len(x) != len(y)`` (samples of incomparable length) or ``len(x) < 3`` (insufficient data/degrees of freedom), this error will be thrown.
    """

    if len(x) != len(y):
        raise errors.SampleSizeError(
            f'len(x) == {len(x)} != len(y) == {len(y)}')

    if len(x) < 3:
        raise errors.SampleSizeError(
            f'Sample size of {len(x)} is less than the necessary degrees of freedom (n > 2) for regression estimation.')

    y_mean, x_mean = sample_mean(y), sample_mean(x)

    alpha = y_mean - simple_regression_beta(x=x, y=y)*x_mean
    return alpha


def qq_series_for_sample(sample: list) -> List[list]:
    """
    Calculates the QQ series for a sample of data, i.e. the set defined by the ordered pair of sample percentiles and theoretical normal percentiles. A sample's normality can be assessed by how linear the result graph is.

    Parameters
    ----------
    1. **sample**: ``list``
        A sample of numerical data.
    """
    qq_series = []
    n = len(sample)
    for i in range(len(sample)):
        percentile = (i + 0.5)/n
        percentile_sample = sample_percentile(
            data=sample, percentile=percentile)
        percentile_norm = norm.ppf(q=percentile)
        qq_series += [[percentile_norm, percentile_sample]]

    return qq_series
