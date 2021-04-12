# Examples

## CLI Usage

If I wanted to calculate the risk-return profile for the Facebook (FB), Amazon (AMZN) and Exxon (XOM), I would execute the following command from the project's root directory,

`python main.py -rr FB AMZN XOM`

To list the functions available for pynance, use the <i>-help</i> flag to print a help message, i.e.

`python main.py -help`

Or use the <i>-ex</i> flag to display a list of examples of syntax,

`python main.py -ex`

If you prefer a GUI, most of pynance's functionality has been wired into a PyQt widget GUI that can be launched with,

`python main.py -gui`

The GUI is still in development and so may have a few bugs lurking within it. If you discover one, contact the owner of this repo.

Note, if you put the <i>/scripts/</i> directory on your PATH, it provides a light wrapper around the python invocation so you can dispense with the `python main.py` part of each command. In other words, if <i>/scripts/</i> is on your PATH, you can execute the following command from any directory,

`pynance -opt SPY GLD EWA`

to perform the same operation as the following command performed in the project root directory,

`python main.py -opt SPY GLD EWA`

In addition, some of the functions have extra arguments that can be provided to filter the output. For example, moving averages can be calculated for a range of dates by using the `-start` and `-end` flags, i.e.

`python main.py -mov -start 2020-03-05 -end 2021-02-01 ALLY BX`

will output the (date, average)-tuple series of moving averages defined by the environment variables <b>MA_1</b>, <b>MA_2</b> and <b>MA_3</b> between the dates of 2020-03-05 and 2021-02-01. Note dates must be provided in the <i>YYYY-MM-DD</i> format. As another example, the risk-return profile for a list of equities over a specified date range can be saved to json in the current working directory in the following way,

`python main.py -rr -save "$(pwd)/profile.json" -start "2020-10-02" -end "2021-02-10" MMM UPS LNT LMT `

See

`python main.py -ex`

or

`pynance -ex`

for more examples of additional arguments that can be provided to functions.