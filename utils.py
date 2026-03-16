
def calculate_interaction_likelihood(co_occurrences: int, obs_a: int, obs_b: int) -> float:
    """
    Calculates the likelihood of interaction between two species using the Jaccard Index.

    Args:
        co_occurrences: The number of times the two species were observed
                        within your proximity/time thresholds.
        obs_a: Total number of observations for Species A in that season.
        obs_b: Total number of observations for Species B in that season.

    Returns:
        A float between 0.0 (never interact) and 1.0 (always interact).
    """
    if obs_a == 0 and obs_b == 0:
        return 0.0
    else:
        total_unique_observations = (obs_a + obs_b) - co_occurrences
        likelihood = co_occurrences / total_unique_observations
        return likelihood
