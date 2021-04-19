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

4. Create tabs in GUI for: Markets, Fundamentals, Options, Economy. Markets will feature the portfolio optimization and financial price statistics such as moving averages and efficient frontiers. Fundamentals will feature graphs and calculations of accounting statistics like EBITDA, Enterprise Value, etc. Options will feature functions for calculating IV of options, displaying the volatility skew, historical vs. implied volatility, and option greeks. Economy will feature graphs of the yield curve, GDP, etc. 

5. Copy IV algorithm and option greek algorithms from old python cli program. 

6. TEST MOVING AVERAGE ALGORITHM FOR MIX OF ASSET TYPES. I think there may be some mismatch of types in date comparisons.

7. Correlation algorithm needs tested for mix of asset types as well, i.e. equities and crypto.

8. Create automated tests and integrate repo with a CircleCi pipeline that builds the image. Will need to find a cloud provider to deploy onto. Perhaps [Heroku](https://www.heroku.com/)

16. If an option prices API is found, then IV can be calculated for a specific equity. The optimization algorithm can be expanded to optimize over IV of a portfolio, instead of the Historical Volatility. Allow user to specify what type of volatility the portfolio will use in its optimization, historical or implied. Will need to account for skew, somehow. 

17. Test moving averages plot generation.

18. Pretty sure the reason the len(moving_averages) != len(dates_between) in moving average algorithm is because dates_between doesn't include the dates themselves; it's only returning...dun dun dun...the dates between, not the dates themselves. 

19. Request parameters not being taken to uppercase.

20. Other types of screening. Discounted Cash Flow, for instance. 

21. Add watchlist functionality for crypto assets. Differentiate in /data/common/ between watchlist_equity.json and watchlist_crypto.json. Integrate watchlist functionality into GUI and API. Will need to implement API Key authentication functionality before introducing watchlist to API to account for different users's watchlist.

22. Wire DDM functionality into API. Done. Now Test.

23. Research annotations for cashflow object's growth function and portfolio's return/volatility functions. Perhaps a way of injecting them into the GUI easier. Not sure.

26. Document how to use objects and functions in shell/scripts.

27. Raise Exceptions instead of returning False when functions fail. See #4: https://deepsource.io/blog/8-new-python-antipatterns/

30. Does it make sense to calculate the 'Sharpe Frontier'?

31. Allow relative file references when saving analysis. Right now needs to be absolute path inputted into -save argument. Also, save return profiles. 

32. Export function results as JSON on Angular frontend, i.e. allow users to save results.

33. Facts/opinion tabs.

34. Mark important points of Efficient Frontier, i.e. minimum variance, maximum return, maximum sharpe ratio.

35. Correlation time series.

36. In order for correlation time series to work, the ito_correlation method needs fixed. See TODOS within script.

37. Look into why U risk profile calculation breaks function.

38. Removing chips from risk-profile components should remove them from table.

39. Use recursion estimation for mean, variance and covariance by building from cached values of previous estimates. Remember the statistics are calculated on a rolling 100 day period. Recursion should be derived using a constant number of observations. 

40. Include derivation of recursive estimation in the documentation pages.

41. Build documentation manually with `sphinx-build` and output into nginx root directory where angular project is also located.