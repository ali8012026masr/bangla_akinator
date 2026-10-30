"""Unit tests for Shannon Entropy and Question Selection."""

import math
from app.services.question_selection import (
    compute_entropy,
    calculate_expected_information_gain,
    select_best_question,
)


def test_entropy_properties():
    # Peak distribution (certainty) -> Entropy = 0
    assert abs(compute_entropy([1.0, 0.0, 0.0])) < 1e-6

    # 2 equal outcomes -> 1 bit
    assert abs(compute_entropy([0.5, 0.5]) - 1.0) < 1e-6

    # 4 equal outcomes -> 2 bits
    assert abs(compute_entropy([0.25, 0.25, 0.25, 0.25]) - 2.0) < 1e-6


def test_information_gain_discriminative_vs_useless():
    mock_chars = [
        {"id": "1", "answer_profile": {"q_splits": {"value": True}, "q_useless": {"value": True}}},
        {"id": "2", "answer_profile": {"q_splits": {"value": True}, "q_useless": {"value": True}}},
        {"id": "3", "answer_profile": {"q_splits": {"value": False}, "q_useless": {"value": True}}},
        {"id": "4", "answer_profile": {"q_splits": {"value": False}, "q_useless": {"value": True}}},
    ]
    probs = {"1": 0.25, "2": 0.25, "3": 0.25, "4": 0.25}

    ig_splits = calculate_expected_information_gain("q_splits", mock_chars, probs)
    ig_useless = calculate_expected_information_gain("q_useless", mock_chars, probs)

    assert ig_splits > 0.3
    assert ig_splits > ig_useless
    assert ig_useless < 0.05


def test_select_best_question_deterministic():
    mock_chars = [
        {"id": "1", "answer_profile": {"q_cricketer": {"value": True}, "q_writer": {"value": False}}},
        {"id": "2", "answer_profile": {"q_cricketer": {"value": False}, "q_writer": {"value": True}}},
    ]
    questions = [
        {"question_code": "q_writer", "text_bn": "লেখক?", "order": 2, "active": True},
        {"question_code": "q_cricketer", "text_bn": "ক্রিকেটার?", "order": 1, "active": True},
    ]
    probs = {"1": 0.5, "2": 0.5}

    # Both split equally, but q_cricketer has order=1, so it should be picked deterministically
    best = select_best_question(questions, mock_chars, probs)
    assert best is not None
    assert best["question_code"] == "q_cricketer"
