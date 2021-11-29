from scrilla.static.constants import constants
from scrilla.static import keys
from scrilla.util import dater


def get_trading_period(asset_type: str) -> float:
    """
    Returns the value of one trading day measured in years of the asset_type passed in as an argument.

    Parameters
    ----------
    1. **asset_type**: ``str``

    A string that represents a type of tradeable asset. Types are statically accessible through the ` settings` variables: ASSET_EQUITY and ASSET_CRYPTO.
    """
    if asset_type == keys.keys['ASSETS']['CRYPTO']:
        return constants['ONE_TRADING_DAY']['CRYPTO']
    return constants['ONE_TRADING_DAY']['EQUITY']
