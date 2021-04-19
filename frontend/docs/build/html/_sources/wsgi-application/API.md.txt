# API

## Endpoints
Some endpoints have unique query parameters, but all endpoints accept the following list of query parameters. See below for more information. 

### Query Parameters
- <i>tickers</i>: an array of the stock/crypto tickers (specified by repeated instances of the <i>tickers</i> parameters).<br>
- <i>start</i>: start date of calculation's time period. If not provided, defaults to 100 days ago. Format: YYYY-MM-DD<br>
- <i>end</i>: end date of calculation's time period. If not provided, defaults to today. Format: YYYY-MM-DD<br>
- <i>jpeg</i>: will visualize and return the result as a JPEG. If not provided, defaults to <i>False</i>. Format: true, false. Case insensitive.<br>

1. <h2>/api/risk-return</h2>
    <b>Description</b><br>
    Returns the annualized mean return and the annualized volatility over the specified date range for the supplied list of ticker symbols.<br><br>
    
    <b>Examples</b><br>
    - /api/risk-return?tickers=ALLY&tickers=SNE&tickers=GME<br>
    - /api/risk-return?tickers=TSLA&start=2020-03-22<br><br>
    
    <b>Response JSON</b><br>
    > { <br>
    >    'annual_return': double, <br>
    >    'annual_volatility': double, <br>
    >    'sharpe_ratio': double
    > }<br><br>

2. <h2>/api/optimize</h2>
    <b>Description</b><br>
    Returns the optimal portfolio allocation (i.e. the portfolio with the minimal volatility) for the supplied list of ticker subject to the target return. If no target return is specified, the portfolio's volatility is minimized without constraints.<br><br>
    
    <b>Additional Query Parameters</b><br>
    - <i>target</i>: Optional. The target return subject to which the portfolio will be optimized. If nothing is provided, function will minimize portfolio variance.<br>
    - <i>sharpe</i>: Optional. Defaults to <i>false.</i> If a value of <i>true</i> is provided, the optimization function will <b>maximize</b> the portfolio's Sharpe ratio instead of minimizing the portfolio's volatility.<br><br>
    <b>Examples</b><br>
    - /api/optimize?tickers=SRAC&tickers=SPCE&tickers=AMZN<br>
    - /api/optimize?tickers=FB&tickers=GOOG&tickers=AMZN&tickers=NFLX&target=0.68<br><br>
    
    <b>Response JSON</b><br>
    > {<br>
    >    'portfolio_return': double, <br>
    >    'portfolio_volatility': double,<br>
    >    'allocations': {<br>
    >        &nbsp;&nbsp;&nbsp;&nbsp;'ticker_allocation': double,<br>
    >        &nbsp;&nbsp;&nbsp;&nbsp;'ticker_allocation': double,<br>
    >        &nbsp;&nbsp;&nbsp;&nbsp;...<br>
    >    }<br>
    >}<br>

3. <h2>/api/efficient-frontier</h2>
    <b>Description</b><br>
    Returns the efficient-frontier of a portfolio defined by the supplied list of tickers. Each point on the frontier tier consists of a mean annualized return, an annualized volatility and the portfolio allocations necessary to generate those two statistics.<br><br>

    - <i>sharpe</i>: Optional. Defaults to <i>false.</i> If a value of <i>true</i> is provided, the optimization function will <b>maximize</b> the portfolio's Sharpe ratio instead of minimizing the portfolio's volatility.<br><br>

    <b>Examples</b><br>
    -/api/efficient-frontier?tickers=ENPH&tickers=TTWO&tickers=ATVI&tickers=DE<br><br>

    <b>Response JSON</b><br>
    > {<br>
    >   'portfolio_1': { <br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;'portfolio_return': double, <br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;'portfolio_volatility': double,<br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;'allocations': {<br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'ticker_allocation': double,<br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'ticker_allocation': double,<br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;...<br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;}<br>
    >   },<br>
    >   'portfolio_2': { <br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;'portfolio_return': double,<br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;'portfolio_volatility': double,<br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;'allocations': {<br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'ticker_allocation': double,<br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'ticker_allocation': double,<br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;...<br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;}<br>
    >   },<br>
    >   ...<br>
    > }

4. <h2>/api/moving-averages</h2>
    <b>Description</b><br>
    Returns the moving average of the return over the specified dates. The response will include three moving averages series with periods defined by the <b>MA_1</b>, <b>MA_2</b> and <b>MA_3</b> environment variables. In the future, this endpoint will accept user defined periods through request parameters. Note: if no start-date and end-date are supplied, this endpoint will return a snapshot of the current moving averages, not a time series.<br><br>
    
    <b>Examples</b><br><br>

    <b>Response JSON</b><br>
    > { <br>
    >   'ticker':{ <br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;'ticker_MA_1':{ <br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'date': double, <br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'date': double, <br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;... <br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;}, <br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;'ticker_MA_2:{ <br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'date': double, <br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;... <br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;}, <br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;'ticker_MA_3': { <br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'date': double, <br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;... <br>
    >   &nbsp;&nbsp;&nbsp;&nbsp;}<br>
    > }<br>

5. <h2>/api/discount-dividend-model</h2>
    <b>Description</b><br>
    Returns the discount dividend model price for the given list of equities. Historical dividend prices are regressed against the distribution date and this linear equation is used to project future dividend cash flows. An additional parameter <i>discount</i> (see below) can be used to specify the rate used to discount the modeled future dividend cash flows.<br><br>
    
    <b>Additional Query Parameters</b><br>
    - <i>discount</i>: Optional. The rate of return used to discount future dividend payments. If nothing is provided, the function will default to the cost of equity capital as estimated by the CAPM model.<br><br>
    
    <b>Examples</b><br>

    <b>Response JSON</b><br>

    <b>Note</b><br>
    If the <i>jpeg</i> parameter is specified for this endpoint, the resulting graph will only contain the plot of the first ticker's dividend history and its accompanying linear regression model; only one equity's dividend graphic can be computed and returned at once. The DDM model price will be output onto the graph's legend. <br><br>

    6. <h2>/api/correlation</h2>
    <b>Description</b><br>
    Returns the correlation matrix for the given list of assets (currently supports crypto and equities; cross-correlation between different asset types may still have some hiccups...) over the specific date range. 

    <b>Examples</b><br>

    <b>Response JSON</b><br>

    <b>Note<b><br>
    This endpoint does not currently support the <i>jpeg</i> endpoint parameters. In the future, if provided, the endpoint will return a time series of the correlations. Need to think about how to efficiently calculate such a complex operation.