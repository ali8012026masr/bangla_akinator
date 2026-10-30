"""Comprehensive unit tests for the GameSessionEngine."""

import pytest
import math
from app.services.game_engine import GameSessionEngine, log_sum_exp
from app.models.domain import AnswerEnum, GameStatus, FeedbackEnum
from app.core.errors import SessionStateConflictError


@pytest.fixture
def sample_engine():
    characters = [
        {
            "id": "char_shakib",
            "name_bn": "সাকিব আল হাসান",
            "categories": ["ক্রিকেটার"],
            "answer_profile": {
                "q_sports": {"value": True},
                "q_cricketer": {"value": True},
                "q_writer": {"value": False},
            }
        },
        {
            "id": "char_humayun",
            "name_bn": "হুমায়ূন আহমেদ",
            "categories": ["লেখক"],
            "answer_profile": {
                "q_sports": {"value": False},
                "q_cricketer": {"value": False},
                "q_writer": {"value": True},
            }
        },
        {
            "id": "char_jamal",
            "name_bn": "জামাল ভূঁইয়া",
            "categories": ["ফুটবলার"],
            "answer_profile": {
                "q_sports": {"value": True},
                "q_cricketer": {"value": False},
                "q_writer": {"value": False},
            }
        }
    ]
    questions = [
        {"question_code": "q_sports", "text_bn": "খেলাধুলার সাথে যুক্ত?", "order": 1, "active": True},
        {"question_code": "q_cricketer", "text_bn": "ক্রিকেটার?", "order": 2, "active": True},
        {"question_code": "q_writer", "text_bn": "লেখক?", "order": 3, "active": True},
    ]
    return GameSessionEngine(
        session_id="test_sess_001",
        characters=characters,
        questions=questions,
        status=GameStatus.ASKING,
        min_questions_before_guess=2,
        guess_score_threshold=0.70,
    )


def test_log_sum_exp_stability():
    # Regular values
    assert abs(log_sum_exp([0.0, 0.0]) - math.log(2.0)) < 1e-6

    # Extreme high values that would overflow naive exp
    extreme_large = [1000.0, 1000.0]
    expected = 1000.0 + math.log(2.0)
    assert abs(log_sum_exp(extreme_large) - expected) < 1e-6

    # Extreme low values
    extreme_small = [-1000.0, -1000.0]
    expected_small = -1000.0 + math.log(2.0)
    assert abs(log_sum_exp(extreme_small) - expected_small) < 1e-6


def test_uniform_prior_probabilities(sample_engine):
    probs = sample_engine.get_probabilities()
    assert len(probs) == 3
    # 3 characters -> each should start with probability 1/3
    for p in probs.values():
        assert abs(p - 1.0 / 3.0) < 1e-4


def test_bayesian_updates_and_ranking(sample_engine):
    sample_engine.current_question_code = "q_sports"
    sample_engine.record_answer("q_sports", AnswerEnum.YES)

    probs = sample_engine.get_probabilities()
    # Shakib & Jamal have q_sports=True, Humayun has q_sports=False
    assert probs["char_shakib"] > probs["char_humayun"]
    assert probs["char_jamal"] > probs["char_humayun"]

    # Next question
    sample_engine.current_question_code = "q_cricketer"
    sample_engine.record_answer("q_cricketer", AnswerEnum.YES)

    probs2 = sample_engine.get_probabilities()
    # Now Shakib should strongly dominate
    assert probs2["char_shakib"] > 0.80

    top_char, score = sample_engine.get_top_candidate()
    assert top_char["id"] == "char_shakib"
    assert score > 0.80


def test_min_questions_enforced(sample_engine):
    # Set min_questions = 3
    sample_engine.min_questions_before_guess = 3
    sample_engine.current_question_code = "q_cricketer"
    sample_engine.record_answer("q_cricketer", AnswerEnum.YES)

    # Only 1 question asked, so evaluate_next_step MUST NOT guess yet
    step = sample_engine.evaluate_next_step()
    assert step["status"] == GameStatus.ASKING
    assert step["next_question"] is not None
    assert step["guess"] is None


def test_guess_trigger_and_correct_feedback(sample_engine):
    sample_engine.min_questions_before_guess = 1
    sample_engine.current_question_code = "q_cricketer"
    sample_engine.record_answer("q_cricketer", AnswerEnum.YES)

    step = sample_engine.evaluate_next_step()
    assert step["status"] == GameStatus.GUESS_PENDING
    assert step["guess"]["name_bn"] == "সাকিব আল হাসান"

    # User confirms guess was correct
    feedback_result = sample_engine.handle_guess_feedback(
        FeedbackEnum.CORRECT,
        proposed_character_id=step["guess"]["character_id"]
    )
    assert feedback_result["status"] == GameStatus.WON
    assert sample_engine.status == GameStatus.WON


def test_rejected_guess_not_repeated(sample_engine):
    sample_engine.min_questions_before_guess = 1
    sample_engine.current_question_code = "q_cricketer"
    sample_engine.record_answer("q_cricketer", AnswerEnum.YES)

    step = sample_engine.evaluate_next_step()
    shakib_id = step["guess"]["character_id"]

    # User says WRONG!
    feedback = sample_engine.handle_guess_feedback(
        FeedbackEnum.WRONG,
        proposed_character_id=shakib_id
    )
    # Rejected id must be recorded
    assert shakib_id in sample_engine.rejected_character_ids

    # Top candidate excluding Shakib must now be someone else (e.g. Jamal)
    next_top, next_score = sample_engine.get_top_candidate()
    assert next_top is not None
    assert next_top["id"] != shakib_id


def test_invalid_state_and_out_of_order_errors(sample_engine):
    # Attempting to answer a question that wasn't current
    sample_engine.current_question_code = "q_sports"
    with pytest.raises(SessionStateConflictError):
        sample_engine.record_answer("q_writer", AnswerEnum.YES)

    # Attempting feedback when not in GUESS_PENDING
    sample_engine.status = GameStatus.ASKING
    with pytest.raises(SessionStateConflictError):
        sample_engine.handle_guess_feedback(FeedbackEnum.CORRECT, "any_id")
