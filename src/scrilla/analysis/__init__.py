r"""
This module is a toolset for financial and statistical analysis. The top level functions provide general functionality, like universal statistical estimators, financial ratios and calculation techniques. Every calculation that occurs in this module assumes two things:
    1. An estimation method.
        This determines how the sample statistics are calculated from sample data. `scrilla` can be configured to use the [method of moment matching](https://en.wikipedia.org/wiki/Method_of_moments_(statistics)) estimation technique, the [method of percentile matching](https://openacttexts.github.io/Loss-Data-Analytics/C-ModelSelection.html)(section 4.1.3.2), or [maximum likelihood estimation](https://en.wikipedia.org/wiki/Maximum_likelihood_estimation).
    2. A pricing model.
        This determines the type of probability distribution used to model the underlying price processes. Currently, only geometric brownian motion is supported (with future plans for a mean reversion model). 
    
.. notes::
    * I am working on a Bayesian estimation method where estimates of parameters are calculated as the expectation of their respective posterior distribution. 
    * The pricing model is essentially the sampling distribution of Bayesian analysis. The question is how to model the prior distribution. It would make sense if

    $$ p(\mu) = f(r_f, r_m) $$

    where \\(r_f\\) is the risk free rate and \\(r_m\\) is the market rate of return. That is to say, the prior distribution of the mean rate of return is some function of the risk free rate and the market rate. It would make sense if the prior distribution was bounded from below by the risk free rate and concentrated around the market rate of return. An exponential distribution might be appropriate...How to model the prior volatility distribution is a more subtle questions I will need to think about.
"""
