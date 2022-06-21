import json

from typing import Tuple

from scrilla import settings
from scrilla.util import helper
from scrilla.static import keys

MARGINS = 5


def format_stylesheet(sheet):
    theme = get_mode_theme()
    for element in theme:
        sheet = sheet.replace(element, theme[element])

    with open(settings.GUI_ICON_FILE, 'r') as f:
        ICONS = json.load(f)
        for icon in ICONS:
            for state in ICONS[icon]:
                sheet = sheet.replace(
                    f'{icon}-{state}', f'{settings.ASSET_DIR}/{ICONS[icon][state]}')
    return sheet


def get_mode_theme():
    with open(settings.GUI_THEME_FILE, 'r') as f:
        MATERIAL = json.load(f)

    if settings.GUI_DARK_MODE:
        theme_key = 'dark_mode'
    else:
        theme_key = 'light_mode'

    theme = {}
    for i, color in enumerate(MATERIAL[theme_key]):
        for scheme in MATERIAL[color]:
            if i == 0:
                theme[f'$primary-{scheme}'] = MATERIAL[color][scheme]
            elif i == 1:
                theme[f'$accent-{scheme}'] = MATERIAL[color][scheme]
            elif i == 2:
                theme[f'$warn-{scheme}'] = MATERIAL[color][scheme]
    return theme


def get_light_mode_theme():
    with open(settings.GUI_THEME_FILE, 'r') as f:
        MATERIAL = json.load(f)

    light_theme = {}
    for color in MATERIAL['grey']:
        light_theme[f'$primary-{color}'] = MATERIAL['grey'][color]
    for color in MATERIAL['green']:
        light_theme[f'$accent-{color}'] = MATERIAL['green'][color]
    for color in MATERIAL['red']:
        light_theme[f'$warn-{color}'] = MATERIAL['red'][color]

    return light_theme


def format_allocation_profile_title(allocation, portfolio) -> str:
    port_return, port_volatility = portfolio.return_function(
        allocation), portfolio.volatility_function(allocation)
    formatted_result = "("+str(100 *
                               port_return)[:5]+"%, " + str(100*port_volatility)[:5]+"%)"
    formatted_result_title = "("
    for symbol in portfolio.tickers:
        if portfolio.tickers.index(symbol) != (len(portfolio.tickers) - 1):
            formatted_result_title += symbol+", "
        else:
            formatted_result_title += symbol + ") Portfolio Return-Risk Profile"
    whole_thing = formatted_result_title + " = "+formatted_result
    return whole_thing


def format_profile(profile: dict) -> Tuple[str]:
    profile_keys = keys.keys['APP']['PROFILE']
    for key in profile_keys:
        if key in ['RET', 'VOL', 'EQUITY']:
            profile = helper.format_dict_percent(profile, profile_keys[key])
        else:
            profile = helper.format_dict_number(profile, profile_keys[key])
    return profile
