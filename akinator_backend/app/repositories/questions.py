"""Repository for question document operations."""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from app.core.database import get_database


def _format_question(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Format MongoDB question document."""
    if doc and "_id" in doc:
        doc["id"] = str(doc["_id"])
    return doc


class QuestionRepository:
    def __init__(self, db: Optional[Any] = None):
        self._db = db

    @property
    def db(self) -> Any:
        return self._db if self._db is not None else get_database()

    async def get_active_questions(self) -> List[Dict[str, Any]]:
        """Retrieve all active questions ordered by order field."""
        cursor = self.db.questions.find({"active": True}).sort("order", 1)
        questions = await cursor.to_list(length=500)
        return [_format_question(q) for q in questions]

    async def get_by_code(self, question_code: str) -> Optional[Dict[str, Any]]:
        """Fetch question by unique question_code."""
        doc = await self.db.questions.find_one({"question_code": question_code})
        return _format_question(doc) if doc else None

    async def insert_question(self, question_data: Dict[str, Any]) -> str:
        """Insert question with timestamps."""
        now = datetime.now(timezone.utc)
        question_data.setdefault("created_at", now)
        question_data.setdefault("updated_at", now)
        result = await self.db.questions.insert_one(question_data)
        return str(result.inserted_id)

    async def count_active(self) -> int:
        """Count active questions."""
        return await self.db.questions.count_documents({"active": True})
