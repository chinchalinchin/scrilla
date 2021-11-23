import os

from scrilla.util import dater

TEST_DIR = os.path.dirname(os.path.abspath(__file__))

MOCK_DIR = os.path.join(TEST_DIR,'data')

END=dater.parse_date_string("2021-11-19")

START=dater.parse_date_string("2021-07-14")