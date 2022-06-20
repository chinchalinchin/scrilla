import os

from scrilla.util import dater
from scrilla.static import constants

TEST_DIR = os.path.dirname(os.path.abspath(__file__))

MOCK_DIR = os.path.join(TEST_DIR, 'data')

END_STR = "2021-11-19"
END = dater.parse(END_STR)

START_STR = "2021-07-14"
START = dater.parse(START_STR)

def is_within_tolerance(func):
    return (abs(func()) < 10 ** (-constants.constants['ACCURACY']))