import numpy, matplotlib
from PIL import Image

from matplotlib import pyplot as plot
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import util.format as formatter

matplotlib.use("Qt5Agg")

def plot_frontier(portfolio, frontier, show=True, savefile=None):
    title = " ("
    for i in range(len(portfolio.tickers)):
        if i != (len(portfolio.tickers) - 1):
            title += portfolio.tickers[i] + ", "
        else:
            title += portfolio.tickers[i] + ") Efficient Frontier"
    
    return_profile, risk_profile = [], []
    for allocation in frontier:
        return_profile.append(portfolio.return_function(allocation))
        risk_profile.append(portfolio.volatility_function(allocation))
    
        # don't think numpy arrays are needed...
    # return_profile = numpy.array(return_profile)
    # risk_profile = numpy.array(risk_profile)
    
    canvas = FigureCanvas(Figure())
    axes = canvas.figure.subplots()

    axes.plot(risk_profile, return_profile, linestyle='dashed')
    axes.set_xlabel('Volatility')
    axes.set_ylabel('Return')
    axes.set_title(title)

    if savefile is not None:
        canvas.print_jpeg(filename_or_obj=savefile)

    if show:
        s, (width, height) = canvas.print_to_buffer()
        im = Image.frombytes("RGBA", (width, height), s)
        im.show()
    else:
        return canvas

def plot_profiles(symbols, profiles, show=True, savefile=None):
    canvas = FigureCanvas(Figure())

    no_symbols = len(symbols)
    axes = canvas.figure.subplots()

    title ="("
    for symbol in symbols:
        if symbols.index(symbol) != (len(symbols)-1):
            title += symbol +", "
        else:
            title += symbol +") Risk-Return Profile"

    return_profile, risk_profile = [], []
    for profile in profiles:
        return_profile.append(profile['annual_return'])
        risk_profile.append(profile['annual_volatility'])

    axes.plot(risk_profile, return_profile, linestyle='None', marker= ".", markersize=10.0)
    axes.set_xlabel('Volatility')
    axes.set_ylabel('Return')
    axes.set_title(title)

    for i in range(no_symbols):
        axes.annotate(symbols[i], (risk_profile[i], return_profile[i]))

    if savefile is not None:
        canvas.print_jpeg(filename_or_obj=savefile)

    if show:
        s, (width, height) = canvas.print_to_buffer()
        im = Image.frombytes("RGBA", (width, height), s)
        im.show()
    else:
        return canvas

# TODO: dynamically generate bar or line plot based on number of data points!
# if len(averages) = (# of moving averages)*(# of symbols)
    # create barchart of moving averages as of today
# if len(averages) > (# of moving averages)*(# of symbols)
    # create line plot with three series for all available samples
def plot_moving_averages(symbols, averages, periods, show=True, savefile=None):
    canvas = FigureCanvas(Figure())

    width = formatter.BAR_WIDTH
    x = numpy.arange(len(symbols))
    axes = canvas.figure.subplots()
    
    ma1s, ma2s, ma3s = [], [], []
    for i in range(len(symbols)):
        ma1s.append(averages[i][0])
        ma2s.append(averages[i][1])
        ma3s.append(averages[i][2])
    
    ma1_label, ma2_label, ma3_label = f'MA({periods[0]})', f'MA({periods[1]})', f'MA({periods[2]})'

    axes.bar(x + width, ma1s, width, label=ma1_label)
    axes.bar(x, ma2s, width, label=ma2_label)
    axes.bar(x - width, ma3s, width, label=ma3_label)

    axes.set_ylabel('Moving Average of Daily Return')
    axes.set_title('Moving Averages of Daily Return Grouped By Equity')
    axes.set_xticks(x)
    axes.set_xticklabels(symbols)
    axes.legend()

    if savefile is not None:
        canvas.print_jpeg(filename_or_obj=savefile)

    if show:
        s, (width, height) = canvas.print_to_buffer()
        im = Image.frombytes("RGBA", (width, height), s)
        im.show()
    else:
        return canvas