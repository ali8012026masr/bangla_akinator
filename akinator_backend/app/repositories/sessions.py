"""Repository for persistent game sessions and community contributions."""

from typing import Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from app.core.database import get_database
from app.core.config import settings
from app.models.domain import SessionModel, ContributionModel


def _format_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    if doc and "_id" in doc:
        doc["id"] = str(doc["_id"])
    return doc


class SessionRepository:
    def __init__(self, db: Optional[Any] = None):
        self._db = db

    @property
    def db(self) -> Any:
        return self._db if self._db is not None else get_database()

    async def create_session(self, session: SessionModel) -> str:
        """Persist a new game session with TTL expiration."""
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=settings.SESSION_TTL_MINUTES)

        doc = session.model_dump(exclude={"id"})
        doc["created_at"] = now
        doc["updated_at"] = now
        doc["expires_at"] = expires_at

        result = await self.db.sessions.insert_one(doc)
        return str(result.inserted_id)

    async def get_active_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch session by session_id.
        Explicitly verifies that expires_at has not passed, even before MongoDB's background TTL daemon runs.
        """
        doc = await self.db.sessions.find_one({"session_id": session_id})
        if not doc:
            return None

        # Guard against expired session documents pending TTL deletion
        now = datetime.now(timezone.utc)
        expires_at = doc.get("expires_at")
        if expires_at:
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            if expires_at < now:
                return None

        return _format_doc(doc)

    async def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update session fields and refresh updated_at."""
        now = datetime.now(timezone.utc)
        updates["updated_at"] = now
        # Extend TTL slightly on activity
        updates["expires_at"] = now + timedelta(minutes=settings.SESSION_TTL_MINUTES)

        result = await self.db.sessions.update_one(
            {"session_id": session_id},
            {"$set": updates}
        )
        return result.modified_count > 0

    async def delete_session(self, session_id: str) -> bool:
        """Explicitly remove a session."""
        result = await self.db.sessions.delete_one({"session_id": session_id})
        return result.deleted_count > 0

    async def save_contribution(self, contribution: ContributionModel) -> str:
        """Save a community character contribution under pending_review."""
        now = datetime.now(timezone.utc)
        doc = contribution.model_dump(exclude={"id"})
        doc["created_at"] = now
        result = await self.db.contributions.insert_one(doc)
        return str(result.inserted_id)

    async def find_contribution_by_name(self, normalized_name: str) -> Optional[Dict[str, Any]]:
        """Check if contribution already submitted."""
        doc = await self.db.contributions.find_one({"normalized_name": normalized_name})
        return _format_doc(doc) if doc else None
