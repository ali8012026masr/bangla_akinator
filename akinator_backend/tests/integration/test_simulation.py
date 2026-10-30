"""
End-to-End Game Simulation Tests.
Simulates real player interactions across multiple character archetypes
and verifies Bayesian engine convergence, guess resolution, and community contribution flow.
"""

import pytest
from httpx import AsyncClient, ASGITransport
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.main import app
from app.core.database import get_database


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver"
    ) as ac:
        yield ac


@pytest.mark.asyncio
async def test_full_playthrough_shakib_al_hasan(client: AsyncClient):
    """
    Simulates a player who has 'সাকিব আল হাসান' in mind.
    Answers every question according to Shakib's verified ground truth facts.
    Engine must reach guess_pending and identify Shakib Al Hasan.
    """
    db = get_database()
    shakib_doc = await db.characters.find_one({"normalized_name": "সাকিব আল হাসান"})
    assert shakib_doc is not None, "Shakib Al Hasan must exist in database"
    shakib_profile = shakib_doc.get("answer_profile", {})

    # 1. Start game
    start_resp = await client.post("/api/start-game")
    assert start_resp.status_code == 201
    state = start_resp.json()
    session_id = state["session_id"]
    assert state["status"] == "asking"
    assert "question" in state
    current_q = state["question"]

    step = 0
    max_steps = 25
    game_status = state["status"]
    guess = None

    while game_status == "asking" and step < max_steps:
        step += 1
        q_code = current_q["question_code"]
        fact = shakib_profile.get(q_code)
        
        # Determine answer
        if fact is not None and fact.get("value") is True:
            answer = "YES"
        elif fact is not None and fact.get("value") is False:
            answer = "NO"
        else:
            answer = "UNKNOWN"

        ans_resp = await client.post(
            "/api/answer",
            json={
                "session_id": session_id,
                "question_code": q_code,
                "answer": answer
            }
        )
        assert ans_resp.status_code == 200
        ans_data = ans_resp.json()
        game_status = ans_data["status"]
        current_q = ans_data.get("next_question")
        guess = ans_data.get("guess")

    # Engine must have triggered a guess before or at question limit
    assert game_status == "guess_pending", f"Expected guess_pending, got {game_status}"
    assert guess is not None
    assert guess["name_bn"] == "সাকিব আল হাসান"

    # Confirm the guess
    feedback_resp = await client.post(
        "/api/guess-feedback",
        json={
            "session_id": session_id,
            "feedback": "correct"
        }
    )
    assert feedback_resp.status_code == 200
    won_state = feedback_resp.json()
    assert won_state["status"] == "won"


@pytest.mark.asyncio
async def test_full_playthrough_himu(client: AsyncClient):
    """
    Simulates a player who has fictional character 'হিমু' in mind.
    """
    db = get_database()
    himu_doc = await db.characters.find_one({"normalized_name": "হিমু"})
    assert himu_doc is not None, "Himu must exist in database"
    himu_profile = himu_doc.get("answer_profile", {})

    # 1. Start game
    start_resp = await client.post("/api/start-game")
    assert start_resp.status_code == 201
    state = start_resp.json()
    session_id = state["session_id"]
    current_q = state["question"]
    game_status = state["status"]
    guess = None

    step = 0
    max_steps = 25

    while game_status == "asking" and step < max_steps:
        step += 1
        q_code = current_q["question_code"]
        fact = himu_profile.get(q_code)

        if fact is not None and fact.get("value") is True:
            answer = "YES"
        elif fact is not None and fact.get("value") is False:
            answer = "NO"
        else:
            answer = "UNKNOWN"

        ans_resp = await client.post(
            "/api/answer",
            json={
                "session_id": session_id,
                "question_code": q_code,
                "answer": answer
            }
        )
        assert ans_resp.status_code == 200
        ans_data = ans_resp.json()
        game_status = ans_data["status"]
        current_q = ans_data.get("next_question")
        guess = ans_data.get("guess")

    assert game_status == "guess_pending"
    assert guess is not None
    assert guess["name_bn"] == "হিমু"

    feedback_resp = await client.post(
        "/api/guess-feedback",
        json={
            "session_id": session_id,
            "feedback": "correct"
        }
    )
    assert feedback_resp.status_code == 200
    assert feedback_resp.json()["status"] == "won"


@pytest.mark.asyncio
async def test_defeat_and_community_contribution_flow(client: AsyncClient):
    """
    Simulates a player rejecting guesses or exhausting questions, leading to defeat,
    and then successfully submitting a new Bengali character to moderation queue.
    """
    # 1. Start game
    start_resp = await client.post("/api/start-game")
    assert start_resp.status_code == 201
    state = start_resp.json()
    session_id = state["session_id"]
    current_q = state["question"]
    game_status = state["status"]

    step = 0
    while game_status in ["asking", "guess_pending"] and step < 30:
        step += 1
        if game_status == "asking":
            ans_resp = await client.post(
                "/api/answer",
                json={
                    "session_id": session_id,
                    "question_code": current_q["question_code"],
                    "answer": "UNKNOWN"
                }
            )
            assert ans_resp.status_code == 200
            ans_data = ans_resp.json()
            game_status = ans_data["status"]
            current_q = ans_data.get("next_question")
        elif game_status == "guess_pending":
            fb_resp = await client.post(
                "/api/guess-feedback",
                json={
                    "session_id": session_id,
                    "feedback": "wrong"
                }
            )
            assert fb_resp.status_code == 200
            fb_data = fb_resp.json()
            game_status = fb_data["status"]
            current_q = fb_data.get("next_question")

    # The game must conclude in defeated or contribution_pending
    assert game_status in ["defeated", "contribution_pending"]

    # Clean up previous test submission if present
    db = get_database()
    await db.contributions.delete_many({"normalized_name": "জাহিদ হাসান"})

    # Player submits an unseeded character
    contrib_payload = {
        "session_id": session_id,
        "name_bn": "জাহিদ হাসান",
        "categories": ["অভিনেতা", "নাট্যকার"]
    }

    contrib_resp = await client.post(
        "/api/contributions",
        json=contrib_payload
    )
    assert contrib_resp.status_code == 201
    contrib_data = contrib_resp.json()
    assert contrib_data["status"] == "pending_review"
    assert contrib_data["contribution_id"] is not None

    # Verify document exists in MongoDB contributions collection
    sub_doc = await db.contributions.find_one({"normalized_name": "জাহিদ হাসান"})
    assert sub_doc is not None
    assert sub_doc["status"] == "pending_review"
    assert sub_doc["session_id"] == session_id
