"""Repository for character document operations."""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from bson import ObjectId
from app.core.database import get_database


def _format_character(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Convert MongoDB document to standard dictionary with string id."""
    if doc and "_id" in doc:
        doc["id"] = str(doc["_id"])
    return doc


class CharacterRepository:
    def __init__(self, db: Optional[Any] = None):
        self._db = db

    @property
    def db(self) -> Any:
        return self._db if self._db is not None else get_database()

    async def get_published_characters(self) -> List[Dict[str, Any]]:
        """Fetch all characters with status='published'."""
        cursor = self.db.characters.find({"status": "published"})
        characters = await cursor.to_list(length=2000)
        return [_format_character(c) for c in characters]

    async def get_by_id(self, character_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a character by ObjectId string."""
        try:
            doc = await self.db.characters.find_one({"_id": ObjectId(character_id)})
            return _format_character(doc) if doc else None
        except Exception:
            return None

    async def find_by_normalized_name(self, normalized_name: str) -> Optional[Dict[str, Any]]:
        """Find character by normalized name."""
        doc = await self.db.characters.find_one({"normalized_name": normalized_name})
        return _format_character(doc) if doc else None

    async def insert_character(self, character_data: Dict[str, Any]) -> str:
        """Insert a character and return its string ID."""
        now = datetime.now(timezone.utc)
        character_data.setdefault("created_at", now)
        character_data.setdefault("updated_at", now)
        result = await self.db.characters.insert_one(character_data)
        return str(result.inserted_id)

    async def increment_stats(self, character_id: str, guessed_correctly: bool = False):
        """Atomically increment times_played and optional times_guessed_correctly."""
        inc_fields: Dict[str, int] = {"times_played": 1}
        if guessed_correctly:
            inc_fields["times_guessed_correctly"] = 1

        try:
            await self.db.characters.update_one(
                {"_id": ObjectId(character_id)},
                {"$inc": inc_fields, "$set": {"updated_at": datetime.now(timezone.utc)}}
            )
        except Exception:
            pass
