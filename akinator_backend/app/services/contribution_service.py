"""
Service layer for managing community character submissions.
Enforces normalization, duplicate detection, and review queue isolation.
"""

import unicodedata
from typing import Dict, Any, Optional
from app.repositories.characters import CharacterRepository
from app.repositories.sessions import SessionRepository
from app.models.domain import ContributionModel
from app.core.errors import AppException


def normalize_bengali_text(text: str) -> str:
    """Normalize Unicode Bengali string and strip surrounding whitespace."""
    if not text:
        return ""
    # NFC normalization for consistent Bengali conjuncts
    normalized = unicodedata.normalize("NFC", text.strip())
    # Collapse multiple internal spaces
    return " ".join(normalized.split())


class ContributionService:
    def __init__(
        self,
        character_repo: Optional[CharacterRepository] = None,
        session_repo: Optional[SessionRepository] = None
    ):
        self.character_repo = character_repo or CharacterRepository()
        self.session_repo = session_repo or SessionRepository()

    async def submit_contribution(
        self,
        session_id: str,
        name_bn: str,
        categories: list[str],
        answer_history: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate, deduplicate, and store a proposed character for moderation.
        """
        normalized = normalize_bengali_text(name_bn)
        if len(normalized) < 2:
            raise AppException(
                error_code="INVALID_CHARACTER_NAME",
                message="Character name is too short.",
                message_bn="চরিত্রের নাম অত্যন্ত সংক্ষিপ্ত।",
                status_code=422
            )

        # 1. Check if character already exists in published canonical characters
        existing_char = await self.character_repo.find_by_normalized_name(normalized)
        if existing_char:
            return {
                "status": "already_exists",
                "contribution_id": existing_char["id"],
                "message_bn": f"'{name_bn}' চরিত্রটি ইতোমধ্যে আমাদের ডাটাবেসে বিদ্যমান আছে! পরবর্তীতে জ্বিন এটি আরও ভালোভাবে অনুমান করার চেষ্টা করবে।"
            }

        # 2. Check if already submitted and pending review
        existing_contrib = await self.session_repo.find_contribution_by_name(normalized)
        if existing_contrib:
            return {
                "status": "pending_review",
                "contribution_id": existing_contrib["id"],
                "message_bn": f"ধন্যবাদ! '{name_bn}' চরিত্রটি ইতোমধ্যে পর্যালোচনার জন্য জমা রয়েছে।"
            }

        # 3. Create new pending contribution
        cleaned_categories = [normalize_bengali_text(c) for c in categories if c.strip()]
        if not cleaned_categories:
            cleaned_categories = ["অন্যান্য"]

        contribution = ContributionModel(
            session_id=session_id,
            name_bn=normalized,
            normalized_name=normalized,
            categories=cleaned_categories,
            answer_history=answer_history,
            status="pending_review",
        )

        contrib_id = await self.session_repo.save_contribution(contribution)
        return {
            "status": "pending_review",
            "contribution_id": contrib_id,
            "message_bn": f"ধন্যবাদ! '{name_bn}' চরিত্রটি পর্যালোচনার জন্য জমা হয়েছে। পর্যালোচনার পর এটি জ্বিনের জ্ঞানে যুক্ত হবে।"
        }
