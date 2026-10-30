"""Async MongoDB connection and index management using official PyMongo Async API."""

import asyncio
from typing import Optional, Any
from pymongo import AsyncMongoClient
import pymongo
from app.core.config import settings
from app.core.logging_config import logger

_client: Optional[AsyncMongoClient] = None


def get_mongo_client() -> AsyncMongoClient:
    """Return or create an AsyncMongoClient bound to the current running event loop."""
    global _client
    try:
        current_loop = asyncio.get_running_loop()
    except RuntimeError:
        current_loop = None

    # Reconnect if client doesn't exist or was created on a different event loop (e.g. across test fixtures)
    if _client is None or (current_loop and getattr(_client, "_loop", None) != current_loop):
        _client = AsyncMongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=5000)
    return _client


def get_database(client: Optional[AsyncMongoClient] = None) -> Any:
    """Return database instance."""
    if client is None:
        client = get_mongo_client()
    return client[settings.DB_NAME]


async def close_database_connection():
    """Close MongoDB client connection cleanly."""
    global _client
    if _client is not None:
        await _client.close()
        _client = None
        logger.info("MongoDB connection closed cleanly.")


async def init_db_indexes(db: Optional[Any] = None):
    """
    Initialize and verify all database indexes and uniqueness constraints.
    Idempotent operation that avoids name collision conflicts.
    """
    if db is None:
        db = get_database()

    logger.info("Ensuring database indexes...")

    async def ensure_index(col, keys, unique=False, ttl=None, partial=None):
        existing = await col.index_information()
        for idx_name, idx_info in existing.items():
            if idx_info.get("key") == keys:
                return
        
        kwargs = {}
        if unique:
            kwargs["unique"] = True
        if ttl is not None:
            kwargs["expireAfterSeconds"] = ttl
        if partial is not None:
            kwargs["partialFilterExpression"] = partial
        await col.create_index(keys, **kwargs)

    # 1. Questions collection
    await ensure_index(db.questions, [("question_code", pymongo.ASCENDING)], unique=True)
    await ensure_index(db.questions, [("active", pymongo.ASCENDING)])

    # 2. Characters collection
    await ensure_index(
        db.characters,
        [("normalized_name", pymongo.ASCENDING)],
        unique=True,
        partial={"status": "published"}
    )
    await ensure_index(db.characters, [("status", pymongo.ASCENDING)])
    await ensure_index(db.characters, [("categories", pymongo.ASCENDING)])

    # 3. Sessions collection
    await ensure_index(db.sessions, [("session_id", pymongo.ASCENDING)], unique=True)
    await ensure_index(db.sessions, [("expires_at", pymongo.ASCENDING)], ttl=0)

    # 4. Contributions collection
    await ensure_index(db.contributions, [("status", pymongo.ASCENDING), ("created_at", pymongo.DESCENDING)])
    await ensure_index(db.contributions, [("normalized_name", pymongo.ASCENDING)])

    logger.info("Database indexes successfully verified.")


async def check_db_ready(db: Optional[Any] = None) -> bool:
    """Readiness probe checking MongoDB connection."""
    try:
        if db is None:
            db = get_database()
        await db.command("ping")
        return True
    except Exception as e:
        logger.error(f"MongoDB ping failed: {e}")
        return False
