# Miscellanous Notes

1. All date strings should be converted to <b>datetime.dates</b> at point of contact with user, i.e. in the main.py file where CLI arguments are parsed, within the gui where user arguments are pulled from widgets or in the server's endpoint views where user arguments are provided through query parameters, before passing it the service/statistics/portfolio functions. All functions in the <i>/app/</i> module assume dates are passed in as <b>datetime.dates</b>.

2. The first time the CLI application is invoked, it loads a huge amount of data in the <i>/static/</i> directory. This may take a few moments to complete. Subsequent invocations of the CLI application will not take anywhere near as long.

3. Each layer of the application adds an additional caching mechanism. The <b>CLI</b> application stores service calls and statistical calculations in the <i>/data/cache/</i> folder locally. The <b>WSGI</b> application adds on top of this local caching layer a database caching layer where it stores service calls and statistical calculations. The <b>WSGI</b> will check the database first for calculations and prices before passing it off to the service managers, which in turn will check the local cache for calculations and prices before finally making an external service call for the raw data and proceeding with the calculation.
