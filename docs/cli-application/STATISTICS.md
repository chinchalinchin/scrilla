# Statistics Module

This module provides functions for calculating basic sample statistics for any set of sample data and for quickly calculating statistics on a rolling sample taken from a incrementing time series (See [Rolling Recursive Functions](#Rolling-Recursive-Functions) for more info). In addition, this module also provides functions for calculating fundamental financial statistics using [Ito Calculus](https://en.wikipedia.org/wiki/It%C3%B4_calculus).

1. def sample_mean(x) : <br>
    - [x = Iterable] : Sample of numerical data.<br>
    - <b>Description</b>: <br>

2. def sample_variance(x) : <br> 
    - [x = Iterable] : Sample of numerical data<br>
    - <b>Description</b> : <br> 

3. def sample_covariance(x, y) : <br> 
    - [x = Iterable] : Sample of numerical data<br>
    - [y = Iterable] : Sample of numerical data<br>
    - <b>Notes</b> : `len(x)==len(y)` or else function returns False.<br>
    - <b>Description</b> : <br>

4. def sample_correlation(x, y) : <br>
    - [x = Iterable] : Sample of numerical data<br>
    - [y = Iterable] : Sample of numerical data<br>
    - <b>Notes</b> : `len(x)==len(y)` or else function returns False.<br>
    - <b>Description</b> : <br>

5. def regression_beta(x, y) : <br>
    - [x = Iterable] : Sample of independent data<br>
    - [y = Iterable] : Sample of dependent data<br>
    - <b>Notes</b> : `len(x)==len(y)` or else function returns False.<br>
    - <b>Description</b> : <br>

6. def regression_alpha(x, y) : <br>
    - [x = Iterable]<br>
    - [y = Iterable]<br>
    - <b>Notes</b> : `len(x)==len(y)` or else function returns False.<br>
    - <b>Description</b> : <br>

### Rolling Recursive Functions

These functions assume sample statistics are calculated on a rolling sample taken from an incrementing time series. Each time period, the sample gains a new observation and loses its oldest observation. For example, at time <i>t</i>=0 we have the sample [1, 2, 3, 4] and then at time <i>t</i>=1 we lose the first sample of "1" and gain a sample of "5", [2, 3, 4, 5]. These functions will calculate the new value of the given sample statistic in terms of its previous value, the new observation and the lost observation.

1. def recursive_mean(xbar_previous, new_obs, lost_obs, n=settings.DEFAULT_ANALYSIS_PERIOD) : <br>
    - [xbar_previous -> float] : Previous value of the sample mean<br>
    - [new_obs -> float] : New sample observation<br>
    - [lost_obs -> float] : Lost sample observation.<br>
    - [n -> int] : Sample size. Defaults to the value set in the <b>DEFAULT_ANALYSIS_PERIOD</b> environment variable.<br>
    - <b>Description</b> : Recursively calculates the current mean using the previous value of the sample mean, the new observation, the lost observation and the sample size.<br> 
    - <b>Justification</b> :   **LATEX DERIVATION GOES HERE**
    
2. def recursive_variance
3. def recursive_covariance
4. def recursive correlation

### Financial Statistics

1. def calculate_moving_averages
2. def calculate_risk_return
3. def calculate_return_covariance
4. def calculate_ito_correlation
5. def calculate_ito_correlation_series
6. def get_ito_correlation_matrix_string