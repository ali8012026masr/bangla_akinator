"""End-to-End API integration tests using httpx and FastAPI TestClient/ASGITransport."""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver"
    ) as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_and_readiness_endpoints(client: AsyncClient):
    # Liveness
    res_health = await client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json() == {"status": "ok"}

    # Readiness
    res_ready = await client.get("/ready")
    assert res_ready.status_code == 200
    assert res_ready.json()["status"] == "ready"
    assert res_ready.json()["database"] == "connected"


@pytest.mark.asyncio
async def test_full_game_loop_win(client: AsyncClient):
    # 1. Start game
    res_start = await client.post("/api/start-game")
    assert res_start.status_code == 201
    start_data = res_start.json()
    assert "session_id" in start_data
    session_id = start_data["session_id"]
    assert start_data["status"] == "asking"
    assert "question" in start_data
    first_q_code = start_data["question"]["question_code"]

    # 2. Submit answer
    res_ans = await client.post(
        "/api/answer",
        json={
            "session_id": session_id,
            "question_code": first_q_code,
            "answer": "YES"
        }
    )
    assert res_ans.status_code == 200
    ans_data = res_ans.json()
    assert ans_data["status"] in ["asking", "guess_pending"]

    # 3. Recover game state
    res_state = await client.get(f"/api/game-state?session_id={session_id}")
    assert res_state.status_code == 200
    state_data = res_state.json()
    assert state_data["session_id"] == session_id
    assert state_data["question_count"] == 1


@pytest.mark.asyncio
async def test_invalid_and_out_of_order_answer(client: AsyncClient):
    res_start = await client.post("/api/start-game")
    session_id = res_start.json()["session_id"]

    # Invalid answer enum
    res_invalid = await client.post(
        "/api/answer",
        json={
            "session_id": session_id,
            "question_code": "q_is_real_person",
            "answer": "NOT_AN_ENUM_VALUE"
        }
    )
    assert res_invalid.status_code == 422

    # Non-existent session
    res_404 = await client.post(
        "/api/answer",
        json={
            "session_id": "non-existent-session-id",
            "question_code": "q_is_real_person",
            "answer": "YES"
        }
    )
    assert res_404.status_code == 404
    assert res_404.json()["error_code"] == "SESSION_NOT_FOUND"

    # Out of order question code
    res_conflict = await client.post(
        "/api/answer",
        json={
            "session_id": session_id,
            "question_code": "q_non_current_question_code_xyz",
            "answer": "YES"
        }
    )
    assert res_conflict.status_code == 409
    assert res_conflict.json()["error_code"] == "SESSION_STATE_CONFLICT"


@pytest.mark.asyncio
async def test_contributions_pipeline(client: AsyncClient):
    from app.core.database import get_database
    db = get_database()
    await db.contributions.delete_many({"normalized_name": "তাসকিন আহমেদ"})

    res_start = await client.post("/api/start-game")
    session_id = res_start.json()["session_id"]

    # Submit new contribution
    res_contrib = await client.post(
        "/api/contributions",
        json={
            "session_id": session_id,
            "name_bn": "তাসকিন আহমেদ",
            "categories": ["ক্রিকেটার"]
        }
    )
    assert res_contrib.status_code == 201
    data = res_contrib.json()
    assert data["status"] == "pending_review"
    assert "contribution_id" in data
    assert "পর্যালোচনার জন্য জমা হয়েছে" in data["message_bn"]

    # Duplicate contribution attempt
    res_dup = await client.post(
        "/api/contributions",
        json={
            "session_id": session_id,
            "name_bn": "তাসকিন আহমেদ",
            "categories": ["ক্রিকেটার"]
        }
    )
    assert res_dup.status_code == 201
    assert "ইতোমধ্যে পর্যালোচনার জন্য জমা রয়েছে" in res_dup.json()["message_bn"]
