from typing import Tuple

from scrilla import settings
from scrilla.static import constants
from PySide6.QtGui import QFont


STYLES ={
    'TITLE':{
        'font-family': 'Times',
        'font-size': 12,
        'font-weight': QFont.Bold,
        'font-italics': False
    },
    'SUBTITLE':{
        'font-family': 'Times',
        'font-size': 10,
        'font-weight': QFont.DemiBold,
        'font-italics': False
    },
    'TEXT':{
        'font-family': 'Times',
        'font-size': 8,
        'font-weight': QFont.Normal,
        'font-italics': False
    },
    'ERROR': {
        'font-family': 'Helvetica',
        'font-size': 8,
        'font-weight': QFont.Medium,
        'font-italics': False
    }
}

def get_font_style(style_dict: dict) -> QFont:
    """
    Accepts a configuration dictionary and generates a font style for the application.

    Parameters
    ----------
    1. **stlye_dict**: ``dict``
        A dictionary containing configuration for a ``PySide6.QtGui.QFont`` instance. Applications styles are statically accessible through elements of the `scrilla.gui.formats.STYLES` dictionary.
    
    Returns 
    -------
    ``PySide6.QtGui.QFont``
    """
    font = QFont(style_dict['font-family'], style_dict['font-size'])
    font.setWeight(style_dict['font-weight'])
    font.setItalic(style_dict['font-italics'])
    return font

def format_allocation_profile_title(allocation, portfolio) -> str:
    port_return, port_volatility = portfolio.return_function(allocation), portfolio.volatility_function(allocation)
    formatted_result = "("+str(100*port_return)[:5]+"%, " + str(100*port_volatility)[:5]+"%)"
    formatted_result_title = "("
    for symbol in portfolio.tickers:
        if portfolio.tickers.index(symbol) != (len(portfolio.tickers) - 1):
            formatted_result_title += symbol+", "
        else:
            formatted_result_title += symbol + ") Portfolio Return-Risk Profile"
    whole_thing = formatted_result_title +" = "+formatted_result
    return whole_thing

def format_risk_return(stats: dict) -> Tuple[str]:
    formatted_ret = str(100*stats['annual_return'])[:constants.constants['SIG_FIGS']]+"%"
    formatted_vol = str(100*stats['annual_volatility'])[:constants.constants['SIG_FIGS']]+"%"
    return formatted_ret, formatted_vol

def format_correlation(correlation: dict):
    return str(100*correlation["correlation"])[:constants['SIG_FIGS']]+"%"

def calculate_image_width():
    return 4*settings.GUI_WIDTH/5

def calculate_image_height():
    return 4*settings.GUI_HEIGHT/5