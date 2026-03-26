import math

from utils import get_interaction_parameters, haversine_distance_km


def test_empty_lists() -> None:
    """Test when one or both species have no observations."""
    locs_a = []
    locs_b = [("2014-09-21", 43.828, -79.271)]

    co_occur, obs_a, obs_b = get_interaction_parameters(locs_a, locs_b, 0.5)

    assert co_occur == 0
    assert obs_a == 0
    assert obs_b == 1


def test_same_day_close_distance() -> None:
    """Test observations on the same day within the distance threshold."""
    locs_a = [("2017-06-11", 43.6474, -79.4662)]
    locs_b = [("2017-06-11", 43.6480, -79.4670)]

    co_occur, obs_a, obs_b = get_interaction_parameters(locs_a, locs_b, 0.5)

    assert co_occur == 1
    assert obs_a == 1
    assert obs_b == 1


def test_same_day_far_distance() -> None:
    """Test observations on the same day but outside the distance threshold."""
    locs_a = [("2014-09-23", 43.6474, -79.4662)]
    locs_b = [("2014-09-23", 43.4959, -79.5144)]

    co_occur, obs_a, obs_b = get_interaction_parameters(locs_a, locs_b, 0.5)

    assert co_occur == 0
    assert obs_a == 1
    assert obs_b == 1


def test_different_day_close_distance() -> None:
    """Test observations in the exact same location but on different days."""
    locs_a = [("2016-07-11", 43.6474, -79.4662)]
    locs_b = [("2017-06-11", 43.6474, -79.4662)]

    co_occur, obs_a, obs_b = get_interaction_parameters(locs_a, locs_b, 0.5)

    assert co_occur == 0


def test_no_double_counting() -> None:
    """Test that multiple observations of A near one observation of B doesn't inflate interactions."""
    locs_a = [
        ("2017-06-11", 43.6474, -79.4662),
        ("2017-06-11", 43.6475, -79.4665),
        ("2017-06-11", 43.6477, -79.4666)
    ]
    locs_b = [("2017-06-11", 43.6480, -79.4670)]

    co_occur, obs_a, obs_b = get_interaction_parameters(locs_a, locs_b, 0.5)

    assert co_occur == 1
    assert obs_a == 3
    assert obs_b == 1


if __name__ == '__main__':
    import pytest

    pytest.main(['test_utils.py'])
