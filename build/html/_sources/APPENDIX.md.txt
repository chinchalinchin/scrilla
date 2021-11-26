# Appendix

## Notes

1. The following symbols have both equity and crypto assets trading on exchanges:

['ABT', 'AC', 'ADT', 'ADX', 'AE', 'AGI', 'AI', 'AIR', 'AMP', 'AVT', 'BCC', 'BCD', 'BCH', 'BCX', 'BDL', 'BFT', 'BIS', 'BLK', 'BQ', 'BRX', 'BTA', 'BTG', 'CAT', 'CMP', 'CMT', 'CNX', 'CTR', 'CURE', 'DAR', 'DASH', 'DBC', 'DCT', 'DDF', 'DFS', 'DTB', 'DYN', 'EBTC', 'ECC', 'EFL', 'ELA', 'ELF','EMB', 'ENG', 'ENJ', 'EOS', 'EOT', 'EQT', 'ERC', 'ETH', 'ETN', 'EVX', 'EXP', 'FCT', 'FLO', 'FLT', 'FTC', 'FUN', 'GAM', 'GBX', 'GEO', 'GLD', 'GNT', 'GRC', 'GTO', 'INF', 'INS', 'INT', 'IXC', 'KIN', 'LBC', 'LEND', 'LTC', 'MAX', 'MCO', 'MEC', 'MED', 'MGC', 'MINT', 'MLN', 'MNE', 'MOD', 'MSP', 'MTH', 'MTN', 'MUE', 'NAV', 'NEO', 'NEOS', 'NET', 'NMR', 'NOBL', 'NXC', 'OCN', 'OPT', 'PBT', 'PING', 'PPC', 'PPT', 'PRG', 'PRO', 'PST', 'PTC', 'QLC', 'QTUM','R', 'RDN', 'REC', 'RVT', 'SALT', 'SAN', 'SC', 'SKY', 'SLS', 'SPR', 'SNX', 'STK', 'STX', 'SUB', 'SWT', 'THC', 'TKR', 'TRC', 'TRST', 'TRUE', 'TRX', 'TX', 'UNB', 'VERI', 'VIVO', 'VOX', 'VPN', 'VRM', 'VRS', 'VSL', 'VTC', 'VTR', 'WDC', 'WGO', 'WTT', 'XEL', 'NEM', 'ZEN']

Since there is no way good way to distinguish whether or not the asset is an equity or a cryptocurrency based on the value of the ticker alone, the module functions `scrilla.files.get_asset_type` and `scrilla.errors.validate_asset_type` will always default to the equity ticker for the above symbols. 

This is not the greatest solution, as all the crypto symbols given above are inaccessible to analysis. In particular, `ETH` represents a popular crypto that cannot be analyzed, which represents a major failing of the current application.

The way the `service` module works, `PriceManager` can be forced to retrieve the crypto asset's prices instead of the equity asset's through the `services.PriceManager.get_prices` method by providing the method an argument of `asset_type='crypto'`; However, the `service` module function `services.get_daily_price_history`, which is the point of contact between the `PriceManager` and the rest of the application, wraps calls to the `PriceManager.get_prices` method in a cache persistence layer (meaning, `get_daily_price_history` checks if prices exist in the cache before passing the request off to an external service query). The cache doesn't distinguish asset types currently. The `PriceCache` stores prices based on the inputs (<i>ticker, date, open close, close price</i>). So, even if the `PriceManager` is forced to get crypto prices on the first call, subsequent calls to the same `get_daily_price_history` function will likely break the application, or at least lead to misleading results, since the cache will contain a set of prices that doesn't necessarily map one-to-one with its ticker symbol.

If the above problem is to be solved, the cache needs modified to separate prices based on asset type.

2. There is a slight discrepancy between the results of maximum likelihood estimation and moment matching when the underyling distribution of the price process is log-normal. The likelihood algorithm in this library relies on the generalized idea of likelihood estimation; it will compute the log-likelihood function for a given vector of parameters and then optimize that function by varying the vector until the input that produces the maximum output; the usual matter of course is to derive a formula using calculus that can then be analytically solved. Both operations should be equivalent. Moreover, theoretically, it can be shown the maximization operation should be equivalent to the results obtained by the moment matching operation, i.e the maximum likelihood estimator for the mean is the sample mean, etc. However, the results between maximum likelihood estimation and moment matching are off by a few decimal points. It may be due to some vagary of floating point arithmetic, but something else may be going on. See comments in `scrilla.analysis.models.geometric.statistics'


## Documentation

### Dependencies
**Application**
- [dateutil](https://dateutil.readthedocs.io/en/stable/index.html)
- [holidays](https://pypi.org/project/holidays/)
- [matplotlib](https://pypi.org/project/matplotlib/)
- [numpy](https://pypi.org/project/numpy/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [requests](https://pypi.org/project/requests/)
- [scipy](https://pypi.org/project/scipy/)
**GUI**
- [PySide6](https://pypi.org/project/PySide6/)
**Testing**
- [pytest](https://pypi.org/project/pytest/)
- [coverage](https://pypi.org/project/coverage/)
- [httmock](https://pypi.org/project/httmock/)
**Documentation**
- [sphinx](https://pypi.org/project/Sphinx/)
- [pdoc3](https://pypi.org/project/pdoc3/)

**Build**
- [setuptools](https://pypi.org/project/setuptools/)
- [twine](https://pypi.org/project/twine/)
- [build](https://pypi.org/project/build/)

## Assets
- [Ionicons](https://ionic.io/ionicons)