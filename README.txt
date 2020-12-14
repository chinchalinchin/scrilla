Register for an API key at www.alphavantage.co. Create a file named '.env' (no quotesa) in the root directory and place your Alpha Vantage API key within it in an environment variable called,

    AV_QUERY_URL="https://www.alphavantage.co/query?apikey=XXXXX&function=TIME_SERIES_DAILY&symbol"

A 'sample.env' file has been included to demonstrate the appropriate format. Once the API KEY has been set, execute the /app/statistcs.py script and provide the ticker symbols you wish to anaylze. For example, if I wanted to calculate the statistics for the Facebook (FB), Amazon (AMZN) and Exxon (XOM), I would execute the following command from the project's root directory,

    python ./app/pyfin.py FB AMZN XOM