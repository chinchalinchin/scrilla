This is a financial application that calculates asset correlation, statistics and optimal portfolio allocations using data it retrieves from a variety of sources, chief among them AlphaVantage and Quandl. Statistics are calculated using Ito Calculus and should be consistent with the results demanded by Modern Portfolio Theory and Financial Engineering. The portfolios are optimized by minimizing the portfolio's variance/volatility, i.e. by finding the optimal spot on the portfolio's efficient frontier.

The program's functions are wrapped in <b>PyQt5</b> widgets which provide visualizations from <b>matplotlib</b> in addition to the raw output.

# Set Up

First, from the project root directory, (activate your virtual environment, if using one, and) install all of the requirements,

> pip install -r requirements.txt

For the application to retrieve data, it must be connected to AlphaVantage and Quandl. Register for API keys at [AlphaVantage](https://www.alphavantage.co) and [Quandl](https://www.quandl.com/). Create a .env file in the root directory and place your Alpha Vantage and Quandl API keys within it in environment variables called <b>ALPHA_VANTAGE_KEY</b> and <b>QUANDL_KEY</b> respectively. 

There are several other environment variables that configure various aspects of the application. A <i>.sample.env</i> file has been included to demonstrate the appropriate format for all variables, in addition to providing explanations for the other variables that can be changed. Besides the API keys, none of the other environment variables need to be changed from their defaults for the application to function properly. The easiest way to set up is to simply 

> cp .sample.env .env

And then change the <b>ALPHA_VANTAGE_KEY</b> and <b>QUANDL_KEY</b> variables to the values you received when you registered on the respective site. Once the API keys have been set, execute the <i>./main.py script</i>. Supply this script an argument with a dash that specifies the function you wish to execute and the ticker symbols you wish to apply the function to. 

After the application searches for API keys in the <i>.env</i> file, it will search for API keys in <i>config.json</i>. If this file exists, it will override any keys found in <i>.env</i>. If no keys are found within either file, a popup dialog box (QInputDialog from PyQt.QtWidgets) will prompt the user to register for their keys and enter them into a text field. The application will then test the API key entered and if it is valid, save it in the <i>config.json</i> file. Subsequent application calls will leverage the credentials in this file.

## Examples 

If I wanted to calculate the risk-return profile for the Facebook (FB), Amazon (AMZN) and Exxon (XOM), I would execute the following command from the project's root directory,

> python ./main.py -rr FB AMZN XOM

To list the functions available for pynance, use the <i>-help</i> flag to print a help message, i.e.

> python ./main.py -help

Or use the <i>-ex</i> flag to display a list of examples of syntax,

> python ./main.py -ex

If you prefer a GUI, most of pynance's functionality has been wired into a PyQt widget GUI that can be launched with,

> python ./main.py -gui

The GUI is still in development and so may have a few bugs lurking within it. If you discover one, contact the owner of this repo.

Note, if you put the <b>/scripts/</b> directory on your PATH, it provides a light wrapper around the python invocation so you can dispense with the <i>python ./main.py</i> part of each command. In other words, if <b>/scripts/</b> is on your PATH, you can execute the following command from any directory,

> pynance -min SPY GLD EWA

to perform the same operation as the following command performed in the project root directory,

> python ./main.py -min SPY GLD EWA

### TODOS

1. add different price_managers and stat_managers besides AlphaVantage and Quandl.

2. Rejigger moving averages algorithm (calculation and plotting) to accept current snapshot of moving averages and print bar graph (already does this), or accept a history of moving averages and created a line plot with several labeled serieses. Also need to check if date_range is less than any of the MA_PERIODS before proceeding.

3. Rejigger GUI to have DateWidgets to select dates in GUI and take advantage of the new date filtering functionality.

4. Figure out how to launch GUI in Docker, if it's even possible.. Also, volumes.

5. [Free Icons](https://streamlineicons.com/)

6. Cancel button needs to exit application when prompting user for API keys.

7. Return None instead of False when errors are encountered in methods, so methods can have strict typing. Better for documentation! 

### NOTE

The first time this application is run it retrieves a large amount of static data and stores it in the <b>/static/</b> folder. The first call of the function may take some time, but subsequent calls, assuming you do not have the environment variable <b>INIT</b> = <b>True</b>, should not take anywhere near as long.

IMPORTANT: ALL DATE STRINGS SHOULD BE CONVERTED TO DATETIME.DATES AT POINT OF CONTACT WITH USER, I.E. IN THE MAIN.PY FILE OR WITHIN THE GUI SOMEWHERE BEFORE PASSING IT THE SERVICE/STATISTICS/PORTFOLIO FUNCTIONS.