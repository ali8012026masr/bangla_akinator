"""Test fixtures and configurations for pytest."""

import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings
from pymongo import AsyncMongoClient


@pytest.fixture(scope="session")
def test_settings():
    """Returns application settings."""
    return settings


@pytest.fixture(scope="function")
async def test_db():
    """Provides an isolated AsyncMongoClient database connection for async tests."""
    client = AsyncMongoClient(settings.MONGO_URI)
    db = client[settings.DB_NAME]
    yield db
    await client.close()
