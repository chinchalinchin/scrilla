# TODOS

5. Copy IV algorithm and option greek algorithms from old python cli program. 

16. If an option prices API is found, then IV can be calculated for a specific equity. The optimization algorithm can be expanded to optimize over IV of a portfolio, instead of the Historical Volatility. Allow user to specify what type of volatility the portfolio will use in its optimization, historical or implied. Will need to account for skew, somehow. 

17. Test moving averages plot generation.

21. Add watchlist functionality for crypto assets. Differentiate in /data/common/ between watchlist_equity.json and watchlist_crypto.json. Integrate watchlist functionality into GUI and API. 

23. Research annotations for cashflow object's growth function and portfolio's return/volatility functions. Perhaps a way of injecting them into the GUI easier. Not sure.

31. Allow relative file references when saving analysis. Right now needs to be absolute path inputted into -save argument. Also, save return profiles. 

34. Mark important points of Efficient Frontier, i.e. minimum variance, maximum return, maximum sharpe ratio.

35. Correlation time series.

42. review monte carlo simulation. allow value at risk function to specify SDE. look into MLE for parameters.

44. conditional imports based on ANALYSIS_MODE

46. redo statistic operations with vector and matrix operations for greater generalization.

51. don't round crypto shares in portfolio.

52. update references to quandl to nasdaq (they got acquired)

54. juneteenth is getting added to the trading holidays. also, bond markets are closed on columbus day and veterans day. in other words, interest rates are not reported on those days.

55. DYNAMODB CACHE!
    a. role based acess or access keys
    b. initialize tables
    c. figure out optimal indexing strategy
        i. can filter by non-key attributes: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html#DynamoDB.Client.query
    
    Indexing:
    A. Price. Partition: ticker. Sort: date. Filters: method, weekends
    B. Profile. Partition: ticker. Sort: start + end. Filters: method, weekends
    C. Correlation. Partiion: ticker1+ticker2. Sort: start+end. Filters: method, weekends.
    D. Interest. Parition: Maturity. Sort: start+end

56. save api key in /data/common via gui menu (currently just displays dialog without doing anything when clicked)