"""
Seed Data Quality and Discriminative Power Validation Script.
Performs verification on MongoDB collections or in-memory seed records.
"""

import asyncio
import sys
import os
from typing import List, Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import get_database, close_database_connection
from app.core.logging_config import logger


async def validate_database_data() -> bool:
    """Validate data integrity in MongoDB."""
    db = get_database()
    errors: List[str] = []
    warnings: List[str] = []

    questions = await db.questions.find({}).to_list(1000)
    characters = await db.characters.find({}).to_list(1000)

    # 1. Existence checks
    if not questions:
        errors.append("Validation Failure: No questions found in database.")
    if not characters:
        errors.append("Validation Failure: No characters found in database.")

    if errors:
        for err in errors:
            logger.error(err)
        return False

    # 2. Question code uniqueness and structure
    q_codes = set()
    active_q_codes = set()
    for q in questions:
        code = q.get("question_code")
        if not code:
            errors.append(f"Question missing question_code: {q}")
            continue
        if code in q_codes:
            errors.append(f"Duplicate question_code found: {code}")
        q_codes.add(code)

        if not q.get("text_bn"):
            errors.append(f"Question {code} missing Bengali text (text_bn)")
        if q.get("active", False):
            active_q_codes.add(code)

    if not active_q_codes:
        errors.append("No active questions available for game engine.")

    # 3. Character validation
    normalized_names = set()
    published_count = 0

    for c in characters:
        name_bn = c.get("name_bn")
        norm = c.get("normalized_name")
        status = c.get("status")

        if not name_bn:
            errors.append(f"Character document missing name_bn: {c.get('_id')}")
        if not norm:
            errors.append(f"Character '{name_bn}' missing normalized_name")
        elif status == "published":
            if norm in normalized_names:
                errors.append(f"Duplicate published normalized_name: '{norm}'")
            normalized_names.add(norm)
            published_count += 1

        if not c.get("categories") or not isinstance(c.get("categories"), list):
            errors.append(f"Character '{name_bn}' must have non-empty list of categories")

        # Answer profile check
        profile: Dict[str, Any] = c.get("answer_profile", {})
        if len(profile) < 5:
            warnings.append(f"Character '{name_bn}' has sparse answer profile ({len(profile)} answers)")

        for q_code, fact in profile.items():
            if q_code not in q_codes:
                errors.append(f"Character '{name_bn}' references unknown question_code: '{q_code}'")
            if not isinstance(fact, dict) or "value" not in fact or not isinstance(fact["value"], bool):
                errors.append(f"Character '{name_bn}' question '{q_code}' has invalid fact format: {fact}")

    if published_count == 0:
        errors.append("Zero characters with status='published'.")

    # 4. Discriminative Power Check (No question should be 100% True or 100% False across all characters)
    for q_code in active_q_codes:
        trues = 0
        falses = 0
        unknowns = 0
        for c in characters:
            if c.get("status") != "published":
                continue
            fact = c.get("answer_profile", {}).get(q_code)
            if fact is None:
                unknowns += 1
            elif fact.get("value") is True:
                trues += 1
            elif fact.get("value") is False:
                falses += 1

        # A question is completely non-discriminative if either trues == 0 or falses == 0
        if trues == 0 and published_count > 1:
            warnings.append(f"Question '{q_code}' is never True across all {published_count} characters.")
        if falses == 0 and published_count > 1:
            warnings.append(f"Question '{q_code}' is never False across all {published_count} characters.")

    # Report results
    logger.info("=== Seed Data Validation Report ===")
    logger.info(f"Verified {len(questions)} questions ({len(active_q_codes)} active).")
    logger.info(f"Verified {len(characters)} characters ({published_count} published).")

    if warnings:
        logger.warning(f"{len(warnings)} Warnings found:")
        for w in warnings:
            logger.warning(f"  [WARN] {w}")

    if errors:
        logger.error(f"{len(errors)} Errors found:")
        for e in errors:
            logger.error(f"  [ERROR] {e}")
        return False

    logger.info("SUCCESS: All seed data integrity and discriminative checks PASSED.")
    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(validate_database_data())
        if not success:
            sys.exit(1)
    finally:
        asyncio.run(close_database_connection())
