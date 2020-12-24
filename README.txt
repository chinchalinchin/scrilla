Register for an API key at www.alphavantage.co. Create a .env file in the root directory and place your Alpha Vantage API key within it in an environment variable called AV_QUERY_URL. There are several other environment variables that need configured various aspects of the application.

A '.sample.env' file has been included to demonstrate the appropriate format for AV_QUERY_URL (sans API key), in addition to providing explanations for the other environment variables that can be changed. Besides the AV_QUERY_URL, none of the other environment variables need to be changed from their defaults for the application to function properly. 

Once the API KEY has been set, execute the ./main.py script. Supply this script an argument with a dash that specifies the function you wish to execute and the ticker symbols you wish to apply the function to. For example, if I wanted to calculate the risk-return profile for the Facebook (FB), Amazon (AMZN) and Exxon (XOM), I would execute the following command from the project's root directory,

    python ./main.py -rr FB AMZN XOM

To list the functions available for pynance, use the '-help' flag to print a help message, i.e.

    python ./main.py -help

Or use the '-ex' flag to display a list of examples of syntax,

    python ./main.py -ex

Note, if you put the /scripts/ directory on your PATH, it provides a light wrapper around the python invocation so you can dispense with the 'python ./main.py' part of each command. In other words, if /scripts/ is on your PATH, you can execute the following command from any directory,

    pynance -min SPY GLD EWA

to perform the same operation as the following command performed in the project root directory,

    python ./main.py -min SPY GLD EWA

TODOS:

1. Future versions of the application will allow the user to set the service responsible for providing data to the application. Currently, all data is retrieved from the free tier of AlphaVantage.
