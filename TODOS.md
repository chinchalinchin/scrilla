# TODOS

1. Rejigger GUI to have DateWidgets to select dates in GUI and take advantage of the new date filtering functionality.

2. Hook up 'Optimize' widget to optimize subject to constraint.

3. Create functions for calculation and plotting of yield curve. Relevant FRED symbols: 
    - DFF = Effective Federal Funds Rate<br>
    - DTB3 = 3 Month Treasury<br>
    - DGS5 = 5 Year Treasury Constant Maturity<br>
    - DGS10 = 10 Year Treasury Constant Maturity<br>
    - DGS30 = 30 Year Treausry Constant Maturity<br>
    - T5YIE = 5 Year Breakeven Inflation Rate<br>
    - T10YIE = 10 Year Breakeven Inflation Rate<br>

5. Copy IV algorithm and option greek algorithms from old python cli program. 

6. TEST MOVING AVERAGE ALGORITHM FOR MIX OF ASSET TYPES. I think there may be some mismatch of types in date comparisons.

7. Correlation algorithm needs tested for mix of asset types as well, i.e. equities and crypto.

16. If an option prices API is found, then IV can be calculated for a specific equity. The optimization algorithm can be expanded to optimize over IV of a portfolio, instead of the Historical Volatility. Allow user to specify what type of volatility the portfolio will use in its optimization, historical or implied. Will need to account for skew, somehow. 

17. Test moving averages plot generation.

18. Pretty sure the reason the len(moving_averages) != len(dates_between) in moving average algorithm is because dates_between doesn't include the dates themselves; it's only returning...dun dun dun...the dates between, not the dates themselves. 

19. Request parameters not being taken to uppercase.

20. Other types of screening. Discounted Cash Flow, for instance. 

21. Add watchlist functionality for crypto assets. Differentiate in /data/common/ between watchlist_equity.json and watchlist_crypto.json. Integrate watchlist functionality into GUI and API. Will need to implement API Key authentication functionality before introducing watchlist to API to account for different users's watchlist.

23. Research annotations for cashflow object's growth function and portfolio's return/volatility functions. Perhaps a way of injecting them into the GUI easier. Not sure.

26. Document how to use objects and functions in shell/scripts.

27. Raise Exceptions instead of returning False when functions fail. See #4: https://deepsource.io/blog/8-new-python-antipatterns/

30. Does it make sense to calculate the 'Sharpe Frontier'?

31. Allow relative file references when saving analysis. Right now needs to be absolute path inputted into -save argument. Also, save return profiles. 

32. Export function results as JSON on Angular frontend, i.e. allow users to save results.

34. Mark important points of Efficient Frontier, i.e. minimum variance, maximum return, maximum sharpe ratio.

35. Correlation time series.

36. In order for correlation time series to work, the ito_correlation method needs fixed. See TODOS within script.

37. Look into why U risk profile calculation breaks function.

38. Removing chips from risk-profile components should remove them from table.

39. Figure out why recursive estimates of rolling mean returns and volatilitie are off by several decimal spots from their actual values.

40. Include derivation of recursive estimation in the documentation pages.

41. Multiple entries unique entries getting assigned different ids in data_economy data. Must have to do with cache...
41. analysis module can import function module. function module scripts can import each other, as they should be static. analysis module is built out of function module. 
