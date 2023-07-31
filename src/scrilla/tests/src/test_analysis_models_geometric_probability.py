import pytest

from scrilla.analysis.models.geometric import probability

from .. import settings, mock_data


@pytest.mark.parametrize("S0,ST,vol,ret,expiry,d1", mock_data.bs_d1_cases)
def test_d1(S0, ST, vol, ret, expiry, d1):
    this_d1 = probability.d1(S0, ST, vol, ret, expiry)
    assert(settings.is_within_tolerance(lambda: this_d1 - d1))


@pytest.mark.parametrize("S0,ST,vol,ret,expiry,d2", mock_data.bs_d2_cases)
def test_d2(S0, ST, vol, ret, expiry, d2):
    this_d2 = probability.d2(S0, ST, vol, ret, expiry)
    assert(settings.is_within_tolerance(lambda: this_d2 - d2))


@pytest.mark.parametrize("S0,ST,vol,ret,expiry,prob", mock_data.bs_prob_d1_cases)
def test_prob_d1(S0, ST, vol, ret, expiry, prob):
    prob_d1 = probability.prob_d1(S0, ST, vol, ret, expiry)
    assert(settings.is_within_tolerance(lambda: prob_d1 - prob))


@pytest.mark.parametrize("S0,ST,vol,ret,expiry,prob", mock_data.bs_prob_d2_cases)
def test_prob_d2(S0, ST, vol, ret, expiry, prob):
    prob_d2 = probability.prob_d2(S0, ST, vol, ret, expiry)
    assert(settings.is_within_tolerance(lambda: prob_d2 - prob))


@pytest.mark.parametrize("S0,vol,ret,expiry,prob,percentile", mock_data.bs_percentile_cases)
def test_prob_d2(S0, vol, ret, expiry, prob, percentile):
    this_percentile = probability.percentile(S0, vol, ret, expiry, prob)
    assert(settings.is_within_tolerance(lambda: this_percentile - percentile))
