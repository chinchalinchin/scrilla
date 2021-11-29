# TODOS

5. Copy IV algorithm and option greek algorithms from old python cli program. 

16. If an option prices API is found, then IV can be calculated for a specific equity. The optimization algorithm can be expanded to optimize over IV of a portfolio, instead of the Historical Volatility. Allow user to specify what type of volatility the portfolio will use in its optimization, historical or implied. Will need to account for skew, somehow. 

17. Test moving averages plot generation.

20. Other types of screening. Discounted Cash Flow, for instance. 

21. Add watchlist functionality for crypto assets. Differentiate in /data/common/ between watchlist_equity.json and watchlist_crypto.json. Integrate watchlist functionality into GUI and API. Will need to implement API Key authentication functionality before introducing watchlist to API to account for different users's watchlist.

23. Research annotations for cashflow object's growth function and portfolio's return/volatility functions. Perhaps a way of injecting them into the GUI easier. Not sure.

31. Allow relative file references when saving analysis. Right now needs to be absolute path inputted into -save argument. Also, save return profiles. 

34. Mark important points of Efficient Frontier, i.e. minimum variance, maximum return, maximum sharpe ratio.

35. Correlation time series.

37. Look into why U risk profile calculation breaks function.

42. review monte carlo simulation. allow value at risk function to specify SDE. look into MLE for parameters.

44. conditional imports based on ANALYSIS_MODE

46. redo statistic operations with vector and matrix operations for greater generalization.

47. don't import in main.py until you have to.

48. Correlation matrix widget not formatting decimals < 0.01 for some reason. negatives are no go as well.

50. refactor to use math.sqrt from standard library and create dot, multiply and transpose methods for matrices.

51. don't round crypto shares in portfolio.