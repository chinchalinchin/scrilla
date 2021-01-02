import numpy, matplotlib
from PIL import Image

# matplotlib.rcParams['backend.qt4']='PySide'
# matplotlib.use('Qt4Agg')

import matplotlib.pyplot as plot
matplotlib.use("Qt5Agg")

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


import app.settings as settings

def plot_frontier(portfolio, frontier, show=True):
    return_profile=[]
    risk_profile=[]
    for allocation in frontier:
        return_profile.append(portfolio.return_function(allocation))
        risk_profile.append(portfolio.volatility_function(allocation))
    return_profile = numpy.array(return_profile)
    risk_profile = numpy.array(risk_profile)
    
    title = " ( "
    for i in range(len(portfolio.tickers)):
        if i != (len(portfolio.tickers) - 1):
            title += portfolio.tickers[i] + ", "
        else:
            title += portfolio.tickers[i] + " ) Efficient Frontier"
    
    fig, ax = plot.subplots()

    ax.plot(risk_profile, return_profile, linestyle='dashed')
    ax.set_xlabel('Volatility')
    ax.set_ylabel('Return')
    ax.set_title(title)

    if show:
        plot.show()
    else:
        return fig

def plot_moving_averages(symbols, averages, show=True):
    figure = Figure(figsize=(5,3))    
    canvas = FigureCanvas(figure)

    width = settings.BAR_WIDTH
    x = numpy.arange(len(symbols))
    axes = canvas.figure.subplots()
    
    ma1s, ma2s, ma3s = [], [], []
    for i in range(len(symbols)):
        ma1s.append(averages[i][0])
        ma2s.append(averages[i][1])
        ma3s.append(averages[i][2])
    
    ma1_label, ma2_label, ma3_label = f'MA({settings.MA_1_PERIOD})', f'MA({settings.MA_2_PERIOD})', f'MA({settings.MA_3_PERIOD})'
    axes.bar(x + width, ma1s, width, label=ma1_label)
    axes.bar(x, ma2s, width, label=ma2_label)
    axes.bar(x - width, ma3s, width, label=ma3_label)

    axes.set_ylabel('Moving Average of Daily Return')
    axes.set_title('Moving Averages of Daily Return Grouped By Equity')
    axes.set_xticks(x)
    axes.set_xticklabels(symbols)
    axes.legend()

    if show:
        s, (width, height) = canvas.print_to_buffer()
        im = Image.frombytes("RGBA", (width, height), s)
        im.show()
    else:
        return canvas