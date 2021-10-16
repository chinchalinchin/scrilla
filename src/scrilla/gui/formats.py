import json

from typing import Tuple

from scrilla import settings
from scrilla.gui.widgets.functions import CorrelationWidget, DiscountDividendWidget, DistributionWidget, \
                                            EfficientFrontierWidget, MovingAverageWidget, OptimizerWidget, \
                                            RiskProfileWidget, YieldCurveWidget
from scrilla.util import helper
from scrilla.static import keys

FUNC_WIDGETS= {
    'correlation':{
        'name': 'Correlation Matrix',
        'class': CorrelationWidget,
        'shortcut': 'Ctrl+1',
        'group': 'analysis'
    },
    'dividend': {
        'name': 'Discount Discount Model',
        'class': DiscountDividendWidget,
        'shortcut':'Ctrl+2',
        'group': 'analysis'
    },
    'frontier': {
        'name': 'Efficient Frontiers',
        'class': MovingAverageWidget,
        'shortcut': 'Ctrl+3',
        'group': 'analysis'
    },
    'averages':{
        'name': 'Moving Averages',
        'class': OptimizerWidget,
        'shortcut': 'Ctrl+4',
        'group': 'analysis'
    },
    'optimize':{
        'name': 'Portfolio Optimization',
        'class': DistributionWidget,
        'shortcut': 'Ctrl+5',
        'group': 'allocation'
    },
    'distribution':{
        'name': 'Return Distribution',
        'class': DistributionWidget,
        'shortcut': 'Ctrl+7',
        'group': 'analysis'
    },
    'risk_profile':{
        'name': 'Risk Profile',
        'class': RiskProfileWidget,
        'shortcut': 'Ctrl+8',
        'group': 'analysis'

    }
}

MENUBAR_WIDGET={
    'File': [ {
        'name': 'Add API Key',
        'shortcut': 'Ctrl+A', 
    }],
    'Functions' : [ {
        'name': FUNC_WIDGETS[func_widget]['name'], 
        'shortcut': FUNC_WIDGETS[func_widget]['shortcut']
        } for func_widget in FUNC_WIDGETS
    ],
    'View': [ {
        'name': 'Function Menu',
        'shortcut': 'Ctrl+F'
    }]
}

MARGINS = 5


def format_stylesheet(sheet):
    if settings.GUI_DARK_MODE:
        mode = get_dark_mode_theme()
    else:
        mode = get_light_mode_theme()

    for element in mode:
        sheet = sheet.replace(element, mode[element])

    return sheet

def get_dark_mode_theme():
    with open(settings.GUI_THEME_FILE, 'r') as f:
        MATERIAL = json.load(f)

    dark_theme = {}
    for color in MATERIAL['grey']:
        dark_theme[f'$primary-{color}']= MATERIAL['grey'][color]
    for color in MATERIAL['green']:
        dark_theme[f'$accent-{color}'] = MATERIAL['green'][color]
    for color in MATERIAL['red']:
        dark_theme[f'$warn-{color}'] = MATERIAL['red'][color]

    return dark_theme

def get_light_mode_theme():
    with open(settings.GUI_THEME_FILE, 'r') as f:
        MATERIAL = json.load(f)
        
    light_theme = {}
    for color in MATERIAL['grey']:
        light_theme[f'$primary-{color}']= MATERIAL['grey'][color]
    for color in MATERIAL['green']:
        light_theme[f'$accent-{color}'] = MATERIAL['green'][color]
    for color in MATERIAL['red']:
        light_theme[f'$warn-{color}'] = MATERIAL['red'][color]

    return light_theme

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

def format_profile(profile: dict) -> Tuple[str]:
    profile_keys = keys.keys['APP']['PROFILE']
    for key in profile_keys:
        if key in ['RET', 'VOL', 'EQUITY']:
            profile = helper.format_dict_percent(profile, profile_keys[key])
        else:
            profile = helper.format_dict_number(profile, profile_keys[key])
    return profile