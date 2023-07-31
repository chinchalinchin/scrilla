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

44. conditional imports based on ANALYSIS_MODE once reversion mode is implemented
    -> implement reversion mode

46. redo statistic operations with vector and matrix operations for greater generalization.

51. don't round crypto shares in portfolio.

56. save api key in /data/common via gui menu (currently just displays dialog without doing anything when clicked)

57. SHould incorporate inflation in the calculations. (1+Real)(1+Inflation) = (1+Nominal)

58. Implement Welford's recursive algorithm for variance and covariance: https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance (turns out someone already figured it out)

59. clear memory.json when static, common and cache are cleared.

61. pretty sure services and caches should be singletons: https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python

62. pipeline will need service role if it is going to test dynamodb.

62. dynamodb configuration for correlation table is incorrect. primary key is not unique. it will not persist the items correctly. will need to concatenet ticker_1 and ticker_2.
    - > as a result, will need to drop profile and correlations table currently up as they contain incorrect information.

63. internal correlation cache

64. exponential moving averages. also, there has to be a better way of calculating moving averages than the way it is currently being done. research recursive ma algorithms.

<<<<<<< HEAD
65. labels have disappeared from the gui after your brilliant refactoring. great job.
=======
BUGS
----

1. first install, no cache:
    scrilla cvar [ticker] -start <start> -end <end>
    outputs: 
    ```
        Traceback (most recent call last):
    File "/home/chinchalinchin/.local/bin/scrilla", line 8, in <module>
        sys.exit(scrilla())
    File "/home/chinchalinchin/.local/lib/python3.8/site-packages/scrilla/main.py", line 1116, in scrilla
        do_program(sys.argv[1:])
    File "/home/chinchalinchin/.local/lib/python3.8/site-packages/scrilla/main.py", line 1106, in do_program
        validate_function_usage(selection=args['function_arg'],
    File "/home/chinchalinchin/.local/lib/python3.8/site-packages/scrilla/main.py", line 56, in validate_function_usage
        wrapper_function()
    File "/home/chinchalinchin/.local/lib/python3.8/site-packages/scrilla/main.py", line 280, in cli_cvar
        valueatrisk = percentile(S0=latest_price,
    File "/home/chinchalinchin/.local/lib/python3.8/site-packages/scrilla/analysis/models/geometric/probability.py", line 189, in percentile
        return (S0*exp(exponent))
    TypeError: can't multiply sequence by non-int of type 'float'
    ```
    First time, but not after.

2. When you reinstall, it doesn't wipe memory.json from installation dir...
>>>>>>> 56debc10 (update price endpoint)
