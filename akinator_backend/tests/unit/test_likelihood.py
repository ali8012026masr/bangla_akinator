"""Unit tests verifying mathematical consistency of the Likelihood Model."""

import math
from app.models.domain import AnswerEnum, LIKELIHOOD_TABLE


def test_likelihood_values_finite_and_positive():
    """Ensure all likelihoods are strictly positive and finite."""
    for (fact, answer), val in LIKELIHOOD_TABLE.items():
        assert isinstance(val, (int, float))
        assert val > 0.0, f"Likelihood for {(fact, answer)} must be > 0"
        assert val <= 1.0, f"Likelihood for {(fact, answer)} must be <= 1"
        assert not math.isnan(val)
        assert not math.isinf(val)

    # Law of Total Probability: Each condition must sum to 1.0 across all 5 answers
    for fact in [True, False, None]:
        total_p = sum(LIKELIHOOD_TABLE[(fact, ans)] for ans in AnswerEnum)
        assert abs(total_p - 1.0) < 1e-6, f"Conditional probability for fact={fact} must sum to 1.0, got {total_p}"


def test_discriminative_directional_properties():
    """Verify that YES supports TRUE facts and NO supports FALSE facts."""
    # YES should strongly support True fact over False fact
    assert LIKELIHOOD_TABLE[(True, AnswerEnum.YES)] > LIKELIHOOD_TABLE[(False, AnswerEnum.YES)]

    # NO should strongly support False fact over True fact
    assert LIKELIHOOD_TABLE[(False, AnswerEnum.NO)] > LIKELIHOOD_TABLE[(True, AnswerEnum.NO)]

    # Probably YES should be ordered between YES and UNKNOWN
    assert (
        LIKELIHOOD_TABLE[(True, AnswerEnum.YES)]
        > LIKELIHOOD_TABLE[(True, AnswerEnum.PROBABLY_YES)]
        > LIKELIHOOD_TABLE[(True, AnswerEnum.UNKNOWN)]
    )


def test_missing_fact_neutrality():
    """Unknown fact should offer neutral, low-information updates."""
    # Likelihood of YES and NO given an unknown fact should be symmetric and equal
    assert LIKELIHOOD_TABLE[(None, AnswerEnum.YES)] == LIKELIHOOD_TABLE[(None, AnswerEnum.NO)]
    assert LIKELIHOOD_TABLE[(None, AnswerEnum.PROBABLY_YES)] == LIKELIHOOD_TABLE[(None, AnswerEnum.PROBABLY_NO)]
