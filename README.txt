Register for an API key at www.alphavantage.co. Create a file named '.env' (no quotesa) in the root directory and place your Alpha Vantage API key within it in an environment variable called,

    AV_QUERY_URL="https://www.alphavantage.co/query?apikey=XXXXX&function=TIME_SERIES_DAILY&symbol"

A 'sample.env' file has been included to demonstrate the appropriate format. Once the API KEY has been set, execute the ./main.py script. Supply this script an argument with a dash that specifies the function you wish to execute and the ticker symbols you wish to apply the function to. For example, if I wanted to calculate the risk-return profile for the Facebook (FB), Amazon (AMZN) and Exxon (XOM), I would execute the following command from the project's root directory,

    python ./main.py -s FB AMZN XOM

To list the functions available for pynance, use the '-h' flag to print a help message, i.e.

    python ./main.py -h

[[1, 0.5183987856417677, 0.35282631455695634, 0.33624850022234604], [0.5183987856417677, 1, 0.6317555166094494, 0.12155109270546714], [0.35282631455695634, 0.6317555166094494, 1, -0.10496594811303127], [0.33624850022234604, 0.12155109270546714, -0.10496594811303127, 1]]

