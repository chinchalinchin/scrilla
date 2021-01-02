This is a financial application that calculates asset correlation, statistics and optimal portfolio allocations using data it retrieves from a variety of sources, chief among them AlphaVantage and Quandl.

For the application to retrieve data, it must be connected to AlphaVantage and Quandl. Register for API keys at https://www.alphavantage.co and https://www.quandl.com/. Create a .env file in the root directory and place your Alpha Vantage and Quandl API keys within it in environment variables called ALPHA_VANTAGE_KEY and QUANDL_KEY respectively. 

There are several other environment variables that configure various aspects of the application. A '.sample.env' file has been included to demonstrate the appropriate format for all variables, in addition to providing explanations for the other variables that can be changed. Besides the API keys, none of the other environment variables need to be changed from their defaults for the application to function properly. The easiest way to set up is to simply 

    cp .sample.env .env

And then change the ALPHA_VANTAGE_KEY and QUANDL_KEY variables to the values you received when you registered on the respective site. Once the API keys have been set, execute the ./main.py script. Supply this script an argument with a dash that specifies the function you wish to execute and the ticker symbols you wish to apply the function to. For example, if I wanted to calculate the risk-return profile for the Facebook (FB), Amazon (AMZN) and Exxon (XOM), I would execute the following command from the project's root directory,

    python ./main.py -rr FB AMZN XOM

To list the functions available for pynance, use the '-help' flag to print a help message, i.e.

    python ./main.py -help

Or use the '-ex' flag to display a list of examples of syntax,

    python ./main.py -ex

If you prefer a GUI, most of pynance's functionality has been wired into a PyQt widget GUI that can be launched with,

    python ./main.py -gui

The GUI is still in development and so may have a few bugs lurking within it. If you discover one, contact the owner of this repo.

Note, if you put the /scripts/ directory on your PATH, it provides a light wrapper around the python invocation so you can dispense with the 'python ./main.py' part of each command. In other words, if /scripts/ is on your PATH, you can execute the following command from any directory,

    pynance -min SPY GLD EWA

to perform the same operation as the following command performed in the project root directory,

    python ./main.py -min SPY GLD EWA

TODOS:

1. Future versions of the application will allow the user to set the service responsible for providing data to the application. Currently, all data is retrieved from the free tier of AlphaVantage.

2. Need to rejigger the correlation algorithm so it works across asset types. Currently only works if assets are the same type; things go haywire when asset types are different, presumably because crypto can trade on weekends, screwing up the correlation calculation.

4. Figure out how to launch GUI in Docker. Also, volumes.

5. Free icons: https://streamlineicons.com/

NOTE:

The first time this application is run it retrieves a large amount of static data and stores it in the /static/ folder. The first call of the function may take some time, but subsequent calls, assuming you do not have the environment variable INIT = True, should not take anywhere near as long.