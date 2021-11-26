# This file is part of scrilla: https://github.com/chinchalinchin/scrilla.

# scrilla is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3
# as published by the Free Software Foundation.

# scrilla is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with scrilla.  If not, see <https://www.gnu.org/licenses/>
# or <https://github.com/chinchalinchin/scrilla/blob/develop/main/LICENSE>.

from typing import Tuple, Union
from datetime import date
from scrilla import settings, files
from scrilla.static import keys
from scrilla.util import dater


class InputValidationError(Exception):
    pass


class APIResponseError(Exception):
    pass


class APIKeyError(Exception):
    pass


class ConfigurationError(Exception):
    pass


class SampleSizeError(Exception):
    pass


class PriceError(Exception):
    pass


class UnboundedIntegral(Exception):
    pass


def validate_asset_type(ticker: str, asset_type: Union[str, None] = None) -> str:
    """

    """
    if asset_type is None:
        asset_type = files.get_asset_type(ticker)
        if asset_type is None:
            raise InputValidationError(
                f'{ticker} cannot be mapped to (crypto, equity) asset classes')
        return asset_type
    if asset_type in [keys.keys['ASSETS']['CRYPTO'], keys.keys['ASSETS']['EQUITY'], keys.keys['ASSETS']['BOND']]:
        return asset_type
    raise InputValidationError(
        f'{ticker} cannot be mapped to (crypto, equity) asset classes')


def validate_dates(start_date: date, end_date: date, asset_type: str) -> Tuple[date, date]:
    """

    """

    # if end date exists, make sure it is valid
    if end_date is not None:
        end_date = dater.truncate_future_from_date(end_date)
        if asset_type == keys.keys['ASSETS']['EQUITY']:
            end_date = dater.this_date_or_last_trading_date(end_date)
    # else create a sensible end date
    else:
        if asset_type == keys.keys['ASSETS']['CRYPTO']:
            end_date = dater.today()
        else:
            end_date = dater.get_last_trading_date()

    # if start date exists, make sure it is valide
    if start_date is not None:
        if dater.is_future_date(start_date):
            # only invalid user input is if start date doesn't exist yet
            raise InputValidationError(
                f'Start date of {dater.to_string(start_date)} is greater than today')

        if asset_type == keys.keys['ASSETS']['EQUITY']:
            start_date = dater.this_date_or_last_trading_date(start_date)

    # else create a sensible start date
    else:
        if asset_type == keys.keys['ASSETS']['CRYPTO']:
            start_date = dater.decrement_date_by_days(
                end_date, settings.DEFAULT_ANALYSIS_PERIOD)
        else:
            start_date = dater.decrement_date_by_business_days(
                end_date, settings.DEFAULT_ANALYSIS_PERIOD)

    # verify dates are in order if they exist after dates are possibly changed
    if end_date is not None and start_date is not None:
        start_date, end_date = dater.validate_order_of_dates(
            start_date, end_date)

    return start_date, end_date
