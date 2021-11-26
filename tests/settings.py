import os

from scrilla.util import dater
from scrilla.static import constants

TEST_DIR = os.path.dirname(os.path.abspath(__file__))

MOCK_DIR = os.path.join(TEST_DIR, 'data')

END = dater.parse("2021-11-19")

START = dater.parse("2021-07-14")

def is_within_tolerance(func):
    return (abs(func()) < 10 ** (-constants.constants['ACCURACY']))