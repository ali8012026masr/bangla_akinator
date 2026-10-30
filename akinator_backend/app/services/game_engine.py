"""
Core Probabilistic Game Engine for Bangla Akinator.
Executes log-score Bayesian updates, state transitions, and candidate ranking.
Independent of database and HTTP transport layers.
"""

import math
from typing import List, Dict, Any, Optional, Tuple, Set
from app.models.domain import AnswerEnum, GameStatus, FeedbackEnum, LIKELIHOOD_TABLE
from app.services.question_selection import select_best_question
from app.core.config import settings
from app.core.errors import SessionStateConflictError


def log_sum_exp(log_weights: List[float]) -> float:
    """Compute log(sum(exp(w))) with numerical stability."""
    if not log_weights:
        return float("-inf")
    max_w = max(log_weights)
    if math.isinf(max_w):
        return max_w
    return max_w + math.log(sum(math.exp(w - max_w) for w in log_weights))


class GameSessionEngine:
    def __init__(
        self,
        session_id: str,
        characters: List[Dict[str, Any]],
        questions: List[Dict[str, Any]],
        status: GameStatus = GameStatus.READY,
        asked_question_codes: Optional[List[str]] = None,
        answer_history: Optional[Dict[str, AnswerEnum]] = None,
        candidate_log_weights: Optional[Dict[str, float]] = None,
        rejected_character_ids: Optional[List[str]] = None,
        current_question_code: Optional[str] = None,
        question_count: int = 0,
        max_questions: int = settings.MAX_QUESTIONS,
        min_questions_before_guess: int = settings.MIN_QUESTIONS_BEFORE_GUESS,
        guess_score_threshold: float = settings.GUESS_SCORE_THRESHOLD,
    ):
        self.session_id = session_id
        self.characters = characters
        self.questions = questions
        self.questions_by_code = {q["question_code"]: q for q in questions}
        self.characters_by_id = {str(c["id"]): c for c in characters}

        self.status = status
        self.asked_question_codes = list(asked_question_codes or [])
        self.answer_history = dict(answer_history or {})
        self.rejected_character_ids = set(rejected_character_ids or [])
        self.current_question_code = current_question_code
        self.question_count = question_count

        self.max_questions = max_questions
        self.min_questions_before_guess = min_questions_before_guess
        self.guess_score_threshold = guess_score_threshold

        # Initialize uniform prior: log(1 / N) if not provided
        n_chars = len(characters)
        if not candidate_log_weights:
            prior_log = -math.log(n_chars) if n_chars > 0 else 0.0
            self.candidate_log_weights = {str(c["id"]): prior_log for c in characters}
        else:
            self.candidate_log_weights = dict(candidate_log_weights)

    def get_probabilities(self) -> Dict[str, float]:
        """
        Normalize log-weights into posterior probability distribution:
          P(c) = exp(log_w_c - log_sum_exp(log_weights))
        """
        if not self.candidate_log_weights:
            return {}

        log_weights = list(self.candidate_log_weights.values())
        lse = log_sum_exp(log_weights)

        probs = {}
        for cid, lw in self.candidate_log_weights.items():
            if math.isinf(lw) and lw < 0:
                probs[cid] = 0.0
            else:
                probs[cid] = math.exp(lw - lse)
        return probs

    def get_top_candidate(self, exclude_ids: Optional[Set[str]] = None) -> Tuple[Optional[Dict[str, Any]], float]:
        """
        Return the top eligible character and its posterior match score.
        Excludes rejected characters from being guessed again.
        """
        if exclude_ids is None:
            exclude_ids = self.rejected_character_ids

        probs = self.get_probabilities()
        eligible = [(cid, score) for cid, score in probs.items() if cid not in exclude_ids]

        if not eligible:
            return None, 0.0

        # Sort descending by score, deterministic tie-breaking by character name
        eligible.sort(
            key=lambda item: (item[1], -len(item[0])),
            reverse=True
        )

        top_id, top_score = eligible[0]
        return self.characters_by_id.get(top_id), top_score

    def record_answer(self, question_code: str, answer: AnswerEnum):
        """
        Update candidate log weights based on user answer using categorical likelihood table:
          log_w[c] += log(P(answer | fact_c))
        """
        if self.status != GameStatus.ASKING:
            raise SessionStateConflictError(
                message=f"Cannot submit answer in state '{self.status}'.",
                message_bn="বর্তমান খেলার ধাপে উত্তর গ্রহণ করা সম্ভব নয়।"
            )

        if self.current_question_code and question_code != self.current_question_code:
            raise SessionStateConflictError(
                message=f"Expected answer for '{self.current_question_code}', received '{question_code}'.",
                message_bn="ভুল প্রশ্নের উত্তর প্রদান করা হয়েছে।"
            )

        self.answer_history[question_code] = answer
        if question_code not in self.asked_question_codes:
            self.asked_question_codes.append(question_code)
        self.question_count += 1

        # Bayesian update
        for cid, char in self.characters_by_id.items():
            fact_dict = char.get("answer_profile", {}).get(question_code)
            fact_val = fact_dict.get("value") if isinstance(fact_dict, dict) else None

            likelihood = LIKELIHOOD_TABLE.get((fact_val, answer), 0.20)
            log_lh = math.log(max(likelihood, 1e-6))
            self.candidate_log_weights[cid] += log_lh

    def evaluate_next_step(self) -> Dict[str, Any]:
        """
        Evaluate if we should present a guess, ask the next question, or declare defeat.
        """
        top_char, top_score = self.get_top_candidate()

        # Rule 1: Trigger guess if score meets threshold AND min questions reached
        should_guess_by_score = (
            top_char is not None
            and top_score >= self.guess_score_threshold
            and self.question_count >= self.min_questions_before_guess
        )

        # Rule 2: Force guess if max questions reached and a viable candidate exists
        should_guess_by_limit = (
            top_char is not None
            and self.question_count >= self.max_questions
        )

        if should_guess_by_score or should_guess_by_limit:
            self.status = GameStatus.GUESS_PENDING
            return {
                "status": GameStatus.GUESS_PENDING,
                "next_question": None,
                "guess": {
                    "character_id": str(top_char["id"]),
                    "name_bn": top_char["name_bn"],
                    "categories": top_char.get("categories", []),
                    "image_url": top_char.get("image_url"),
                    "score": round(top_score, 4),
                }
            }

        # Select next best question using Information Gain
        current_probs = self.get_probabilities()
        next_q = select_best_question(
            unasked_questions=self.questions,
            characters=self.characters,
            current_probabilities=current_probs,
            asked_codes=set(self.asked_question_codes)
        )

        if next_q is None:
            # All discriminative questions exhausted without clear candidate
            # If top character has some reasonable score, make a final attempt, else defeat
            if top_char is not None and top_score >= 0.40 and self.question_count >= self.min_questions_before_guess:
                self.status = GameStatus.GUESS_PENDING
                return {
                    "status": GameStatus.GUESS_PENDING,
                    "next_question": None,
                    "guess": {
                        "character_id": str(top_char["id"]),
                        "name_bn": top_char["name_bn"],
                        "categories": top_char.get("categories", []),
                        "image_url": top_char.get("image_url"),
                        "score": round(top_score, 4),
                    }
                }
            self.status = GameStatus.DEFEATED
            return {
                "status": GameStatus.DEFEATED,
                "next_question": None,
                "guess": None
            }

        self.status = GameStatus.ASKING
        self.current_question_code = next_q["question_code"]
        return {
            "status": GameStatus.ASKING,
            "next_question": {
                "question_code": next_q["question_code"],
                "text_bn": next_q["text_bn"],
                "question_number": self.question_count + 1
            },
            "guess": None
        }

    def handle_guess_feedback(self, feedback: FeedbackEnum, proposed_character_id: str) -> Dict[str, Any]:
        """
        Process user confirmation or rejection of the proposed guess.
        """
        if self.status != GameStatus.GUESS_PENDING:
            raise SessionStateConflictError(
                message=f"Cannot submit feedback while game is in state '{self.status}'.",
                message_bn="অনুমানের ফলাফল নিশ্চিত করার উপযুক্ত সময় নয়।"
            )

        if feedback == FeedbackEnum.CORRECT:
            self.status = GameStatus.WON
            return {
                "status": GameStatus.WON,
                "message_bn": "জ্বিন জিতে গেছে! আপনার মনের মানুষটিকে অনুমান করতে পেরেছে! 🧞‍♂️"
            }

        # Guess was WRONG: reject this character from being guessed again
        self.rejected_character_ids.add(proposed_character_id)

        # Check if we can continue asking questions
        if self.question_count >= self.max_questions:
            self.status = GameStatus.DEFEATED
            return {
                "status": GameStatus.DEFEATED,
                "message_bn": "আপনি জ্বিনকে হারিয়েছেন! জ্বিনের অনুমান সঠিক ছিল না।"
            }

        current_probs = self.get_probabilities()
        next_q = select_best_question(
            unasked_questions=self.questions,
            characters=self.characters,
            current_probabilities=current_probs,
            asked_codes=set(self.asked_question_codes)
        )

        if next_q is None:
            self.status = GameStatus.DEFEATED
            return {
                "status": GameStatus.DEFEATED,
                "message_bn": "আপনি জ্বিনকে হারিয়েছেন! আর কোনো প্রশ্ন অবশিষ্ট নেই।"
            }

        self.status = GameStatus.ASKING
        self.current_question_code = next_q["question_code"]
        return {
            "status": GameStatus.ASKING,
            "next_question": {
                "question_code": next_q["question_code"],
                "text_bn": next_q["text_bn"],
                "question_number": self.question_count + 1
            },
            "guess": None
        }
