# Appendix

## Notes

#1
---

The following symbols have both equity and crypto assets trading on exchanges:

['ABT', 'AC', 'ADT', 'ADX', 'AE', 'AGI', 'AI', 'AIR', 'AMP', 'AVT', 'BCC', 'BCD', 'BCH', 'BCX', 'BDL', 'BFT', 'BIS', 'BLK', 'BQ', 'BRX', 'BTA', 'BTG', 'CAT', 'CMP', 'CMT', 'CNX', 'CTR', 'CURE', 'DAR', 'DASH', 'DBC', 'DCT', 'DDF', 'DFS', 'DTB', 'DYN', 'EBTC', 'ECC', 'EFL', 'ELA', 'ELF','EMB', 'ENG', 'ENJ', 'EOS', 'EOT', 'EQT', 'ERC', 'ETH', 'ETN', 'EVX', 'EXP', 'FCT', 'FLO', 'FLT', 'FTC', 'FUN', 'GAM', 'GBX', 'GEO', 'GLD', 'GNT', 'GRC', 'GTO', 'INF', 'INS', 'INT', 'IXC', 'KIN', 'LBC', 'LEND', 'LTC', 'MAX', 'MCO', 'MEC', 'MED', 'MGC', 'MINT', 'MLN', 'MNE', 'MOD', 'MSP', 'MTH', 'MTN', 'MUE', 'NAV', 'NEO', 'NEOS', 'NET', 'NMR', 'NOBL', 'NXC', 'OCN', 'OPT', 'PBT', 'PING', 'PPC', 'PPT', 'PRG', 'PRO', 'PST', 'PTC', 'QLC', 'QTUM','R', 'RDN', 'REC', 'RVT', 'SALT', 'SAN', 'SC', 'SKY', 'SLS', 'SPR', 'SNX', 'STK', 'STX', 'SUB', 'SWT', 'THC', 'TKR', 'TRC', 'TRST', 'TRUE', 'TRX', 'TX', 'UNB', 'VERI', 'VIVO', 'VOX', 'VPN', 'VRM', 'VRS', 'VSL', 'VTC', 'VTR', 'WDC', 'WGO', 'WTT', 'XEL', 'NEM', 'ZEN']

Since there is no way good way to distinguish whether or not the asset is an equity or a cryptocurrency based on the value of the ticker alone, the module functions `scrilla.files.get_asset_type` and `scrilla.errors.validate_asset_type` will always default to the equity ticker for the above symbols. 

This is not the greatest solution, as all the crypto symbols given above are inaccessible to analysis. In particular, `ETH` represents a popular crypto that cannot be analyzed, which represents a major failing of the current application.

The way the `service` module works, `PriceManager` can be forced to retrieve the crypto asset's prices instead of the equity asset's through the `services.PriceManager.get_prices` method by providing the method an argument of `asset_type='crypto'`; However, the `service` module function `services.get_daily_price_history`, which is the point of contact between the `PriceManager` and the rest of the application, wraps calls to the `PriceManager.get_prices` method in a cache persistence layer (meaning, `get_daily_price_history` checks if prices exist in the cache before passing the request off to an external service query). The cache doesn't distinguish asset types currently. The `PriceCache` stores prices based on the inputs (<i>ticker, date, open close, close price</i>). So, even if the `PriceManager` is forced to get crypto prices on the first call, subsequent calls to the same `get_daily_price_history` function will likely break the application, or at least lead to misleading results, since the cache will contain a set of prices that doesn't necessarily map one-to-one with its ticker symbol.

If the above problem is to be solved, the cache needs modified to separate prices based on asset type.

#2
---

There is a slight discrepancy between the results of maximum likelihood estimation and moment matching when the underyling distribution of the price process is log-normal. The likelihood algorithm in this library relies on the generalized idea of likelihood estimation; it will compute the log-likelihood function for a given vector of parameters and then optimize that function by varying the vector until the input that produces the maximum output; the usual matter of course is to derive a formula using calculus that can then be analytically solved. Both operations should be equivalent. Moreover, theoretically, it can be shown the maximization operation should be equivalent to the results obtained by the moment matching operation, i.e the maximum likelihood estimator for the mean is the sample mean, etc. However, the results between maximum likelihood estimation and moment matching are off by a few decimal points. It may be due to some vagary of floating point arithmetic, but something else may be going on. See comments in `scrilla.analysis.models.geometric.statistics'

#3
---

**matplotlib**'s rendering backend does not yet (if it will ever) support the newer **PyQt6**/**PySide6** GUI toolkit and thus requires an older **PyQt5**/**PySide2** dependency. However, the GUI was written in **PySide6** to take advantage of the latest release. Therefore, the application dependencies contain a redundancy. If you examine the [requirements.txt](https://github.com/chinchalinchin/scrilla/blob/develop/main/requirements.txt) dependency file, you will note _both_ **PySide2** and **PySide6** are installed. Until **matplotlib** suports **PySide6**, this unfortunate state of affairs must remain. 

#4
---

The `ORDER BY` clause has not yet been implemented in **PartiQL** (see [GitHub Issue](https://github.com/partiql/partiql-lang-kotlin/issues/47)). As a result, when running in 'dynamodb' _CACHE_MODE_, **PartiQL** queries are sorted application side until this issue is resolved.
 
## Documentation

### Dependencies
**Application**
---------------
- [dateutil](https://dateutil.readthedocs.io/en/stable/index.html)
- [defusedxml]()
- [holidays](https://pypi.org/project/holidays/)
- [matplotlib](https://pypi.org/project/matplotlib/)
- [numpy](https://pypi.org/project/numpy/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [requests](https://pypi.org/project/requests/)
- [scipy](https://pypi.org/project/scipy/)

**GUI**
-------
- [PySide6](https://pypi.org/project/PySide6/)

**Testing**
-----------
- [pytest](https://pypi.org/project/pytest/)
- [coverage](https://pypi.org/project/coverage/)
- [httmock](https://pypi.org/project/httmock/)

**Documentation**
-----------------
- [sphinx](https://pypi.org/project/Sphinx/)
- [pdoc3](https://pypi.org/project/pdoc3/)
- [myst-parser]()

**Build**
---------
- [setuptools](https://pypi.org/project/setuptools/)
- [twine](https://pypi.org/project/twine/)
- [build](https://pypi.org/project/build/)


## References
### Stack Exchanges
- [What Makes A Covariance Matrix Singular](https://stats.stackexchange.com/questions/70899/what-correlation-makes-a-matrix-singular-and-what-are-implications-of-singularit)
- [How to Determine Quantile Isolines of A Multivariate Normal](https://stats.stackexchange.com/questions/64680/how-to-determine-quantiles-isolines-of-a-multivariate-normal-distribution)

### Academic Papers
- [Algorithms for computing sample variance](http://cpsc.yale.edu/sites/default/files/files/tr222.pdf)
- [An Introduction to Copulas](http://www.columbia.edu/~mh2078/QRM/Copulas.pdf)
- [Optimization of Conditional Value At Risk](https://www.ise.ufl.edu/uryasev/files/2011/11/CVaR1_JOR.pdf)
- [Parameter Estimation in Mean Reversion Processes with Deterministic Long-Term Trend](https://www.hindawi.com/journals/jps/2016/5191583/)
- [Updating Formulae and a Pairwise Algorithm For Computing Sample Variances](http://i.stanford.edu/pub/cstr/reports/cs/tr/79/773/CS-TR-79-773.pdf)

### Wikis
- [Algorithms For Calculating Variance](https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance)
- [Empirical Copulas](https://en.wikipedia.org/wiki/Copula_(probability_theory)#Empirical_copulas)
- [Probability Integral Transform](https://en.wikipedia.org/wiki/Probability_integral_transform)
- [Cauchy-Schwarz Inequality](https://en.wikipedia.org/wiki/Cauchy%E2%80%93Schwarz_inequality#Probability_theory)
- [Slyvester Criterion](https://en.wikipedia.org/wiki/Sylvester%27s_criterion)


## Assets
- [Ionicons](https://ionic.io/ionicons)
- [SVGRepo](https://www.svgrepo.com/)