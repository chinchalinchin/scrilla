# NOTES

1. All date strings should be converted to <b>datetime.dates</b> at point of contact with user, i.e. in the main.py file where CLI arguments are parsed, within the gui where user arguments are pulled from widgets or in the server's endpoint views where user arguments are provided through query parameters, before passing it the service/statistics/portfolio functions. All functions in the <i>/app/</i> module assume dates are passed in as <b>datetime.dates</b>.

2. The first time the CLI application is invoked, it loads a huge amount of data in the <i>/static/</i> directory. This may take a few moments to complete. Subsequent invocations of the CLI application will not take anywhere near as long.
