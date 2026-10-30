"""
Question selection using Shannon Entropy and Expected Information Gain.
Operates purely on candidate distributions and likelihood tables without DB dependencies.
"""

import math
from typing import List, Dict, Any, Optional, Set
from app.models.domain import AnswerEnum, LIKELIHOOD_TABLE


def compute_entropy(probabilities: List[float]) -> float:
    """
    Compute Shannon entropy in bits: H(P) = -sum(p * log2(p)).
    p log2(p) is taken as 0 when p == 0.
    """
    entropy = 0.0
    for p in probabilities:
        if p > 1e-12:
            entropy -= p * math.log2(p)
    return entropy


def calculate_expected_information_gain(
    question_code: str,
    characters: List[Dict[str, Any]],
    current_probabilities: Dict[str, float],
) -> float:
    """
    Calculate Expected Information Gain for asking `question_code` across all 5 answers:
      IG(q) = H(Current) - sum_{a in Answers} P(a) * H(Posterior | a)
    """
    char_ids = [str(c["id"]) for c in characters]
    current_probs_list = [current_probabilities.get(cid, 0.0) for cid in char_ids]
    h_current = compute_entropy(current_probs_list)

    if h_current < 1e-6:
        return 0.0

    answers = list(AnswerEnum)
    expected_posterior_entropy = 0.0

    # Fast character fact lookup
    # fact is True, False, or None
    facts = {}
    for c in characters:
        cid = str(c["id"])
        fact_dict = c.get("answer_profile", {}).get(question_code)
        if fact_dict is not None and isinstance(fact_dict, dict):
            facts[cid] = fact_dict.get("value")
        else:
            facts[cid] = None

    for ans in answers:
        # 1. P(ans) = sum_c P(ans | fact_c) * P(c)
        likelihoods = []
        for cid in char_ids:
            fact_val = facts[cid]
            lh = LIKELIHOOD_TABLE.get((fact_val, ans), 0.20)
            likelihoods.append(lh)

        p_ans = sum(lh * p for lh, p in zip(likelihoods, current_probs_list))

        if p_ans < 1e-12:
            continue

        # 2. Posterior P(c | ans) = (P(ans | fact_c) * P(c)) / P(ans)
        posterior_probs = [(lh * p) / p_ans for lh, p in zip(likelihoods, current_probs_list)]
        h_posterior = compute_entropy(posterior_probs)

        expected_posterior_entropy += p_ans * h_posterior

    info_gain = h_current - expected_posterior_entropy
    return max(0.0, info_gain)


def select_best_question(
    unasked_questions: List[Dict[str, Any]],
    characters: List[Dict[str, Any]],
    current_probabilities: Dict[str, float],
    asked_codes: Optional[Set[str]] = None,
) -> Optional[Dict[str, Any]]:
    """
    Select the question that maximizes Expected Information Gain.
    Breaks ties deterministically using question order and code.
    """
    if not unasked_questions or not characters:
        return None

    if asked_codes is None:
        asked_codes = set()

    eligible_questions = [
        q for q in unasked_questions
        if q.get("question_code") not in asked_codes and q.get("active", True)
    ]

    if not eligible_questions:
        return None

    best_question = None
    max_info_gain = -1.0

    for q in eligible_questions:
        q_code = q["question_code"]
        ig = calculate_expected_information_gain(q_code, characters, current_probabilities)

        # Deterministic comparison: higher IG wins; on tie, lower order field or alphabetical code wins
        if ig > max_info_gain + 1e-6:
            max_info_gain = ig
            best_question = q
        elif abs(ig - max_info_gain) <= 1e-6 and best_question is not None:
            q_order = q.get("order", 100)
            best_order = best_question.get("order", 100)
            if (q_order, q_code) < (best_order, best_question["question_code"]):
                best_question = q

    return best_question
