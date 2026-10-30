"""Integration/Unit tests for repositories and database readiness."""

import pytest
from app.core.database import check_db_ready, init_db_indexes
from app.repositories.characters import CharacterRepository
from app.repositories.questions import QuestionRepository
from app.repositories.sessions import SessionRepository
from app.models.domain import SessionModel, GameStatus, AnswerEnum


@pytest.mark.asyncio
async def test_database_ready_probe(test_db):
    ready = await check_db_ready(test_db)
    assert ready is True


@pytest.mark.asyncio
async def test_character_repository_queries(test_db):
    repo = CharacterRepository(test_db)
    characters = await repo.get_published_characters()
    assert len(characters) >= 15

    # Look up Shakib
    shakib = await repo.find_by_normalized_name("সাকিব আল হাসান")
    assert shakib is not None
    assert "ক্রিকেটার" in shakib["categories"]
    assert shakib["answer_profile"]["q_is_cricketer"]["value"] is True

    # Look up by ID
    char_by_id = await repo.get_by_id(shakib["id"])
    assert char_by_id is not None
    assert char_by_id["name_bn"] == "সাকিব আল হাসান"


@pytest.mark.asyncio
async def test_question_repository_queries(test_db):
    repo = QuestionRepository(test_db)
    active_questions = await repo.get_active_questions()
    assert len(active_questions) >= 20

    q_cricketer = await repo.get_by_code("q_is_cricketer")
    assert q_cricketer is not None
    assert q_cricketer["active"] is True
    assert "ক্রিকেটার" in q_cricketer["text_bn"]


@pytest.mark.asyncio
async def test_session_repository_lifecycle(test_db):
    repo = SessionRepository(test_db)
    test_session_id = "test-session-xyz-123"

    session = SessionModel(
        session_id=test_session_id,
        status=GameStatus.ASKING,
        current_question_code="q_is_real_person",
        asked_question_codes=["q_is_real_person"],
        answer_history={"q_is_real_person": AnswerEnum.YES},
        candidate_log_weights={"dummy_id": -0.5},
        question_count=1,
    )

    # 1. Create
    inserted_id = await repo.create_session(session)
    assert inserted_id is not None

    # 2. Retrieve
    retrieved = await repo.get_active_session(test_session_id)
    assert retrieved is not None
    assert retrieved["session_id"] == test_session_id
    assert retrieved["status"] == "asking"

    # 3. Update
    updated = await repo.update_session(test_session_id, {"status": "guess_pending"})
    assert updated is True

    retrieved2 = await repo.get_active_session(test_session_id)
    assert retrieved2["status"] == "guess_pending"

    # 4. Clean up
    deleted = await repo.delete_session(test_session_id)
    assert deleted is True

    retrieved3 = await repo.get_active_session(test_session_id)
    assert retrieved3 is None
