"""API router handling all game endpoints."""

import uuid
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.schemas import (
    StartGameResponse,
    AnswerRequest,
    AnswerResponse,
    GuessFeedbackRequest,
    GuessFeedbackResponse,
    ContributionRequest,
    ContributionResponse,
    GameStateResponse,
    QuestionDTO,
    CharacterGuessDTO,
)
from app.repositories.characters import CharacterRepository
from app.repositories.questions import QuestionRepository
from app.repositories.sessions import SessionRepository
from app.services.game_engine import GameSessionEngine
from app.services.contribution_service import ContributionService
from app.services.question_selection import select_best_question
from app.models.domain import SessionModel, GameStatus, FeedbackEnum
from app.core.errors import SessionNotFoundError, SessionStateConflictError, AppException
from app.core.logging_config import logger

router = APIRouter(tags=["Game"])


# Dependency injection providers
def get_char_repo() -> CharacterRepository:
    return CharacterRepository()


def get_q_repo() -> QuestionRepository:
    return QuestionRepository()


def get_session_repo() -> SessionRepository:
    return SessionRepository()


def get_contrib_service() -> ContributionService:
    return ContributionService()


@router.post("/start-game", response_model=StartGameResponse, status_code=status.HTTP_201_CREATED)
async def start_game(
    char_repo: CharacterRepository = Depends(get_char_repo),
    q_repo: QuestionRepository = Depends(get_q_repo),
    session_repo: SessionRepository = Depends(get_session_repo),
):
    """Initialize a new game session and pick the first question using Information Gain."""
    characters = await char_repo.get_published_characters()
    questions = await q_repo.get_active_questions()

    if not characters:
        raise AppException(
            error_code="NO_CHARACTERS_AVAILABLE",
            message="No published characters in database.",
            message_bn="ডাটাবেসে কোনো সক্রিয় চরিত্র খুঁজে পাওয়া যায়নি।",
            status_code=500
        )
    if not questions:
        raise AppException(
            error_code="NO_QUESTIONS_AVAILABLE",
            message="No active questions in database.",
            message_bn="ডাটাবেসে কোনো সক্রিয় প্রশ্ন খুঁজে পাওয়া যায়নি।",
            status_code=500
        )

    session_id = str(uuid.uuid4())
    engine = GameSessionEngine(
        session_id=session_id,
        characters=characters,
        questions=questions,
        status=GameStatus.ASKING
    )

    # Select the optimal first question
    current_probs = engine.get_probabilities()
    first_q = select_best_question(
        unasked_questions=questions,
        characters=characters,
        current_probabilities=current_probs
    )

    if not first_q:
        raise AppException(
            error_code="INITIAL_QUESTION_FAILED",
            message="Failed to determine starting question.",
            message_bn="প্রথম প্রশ্ন নির্ধারণ করা সম্ভব হয়নি।",
            status_code=500
        )

    engine.current_question_code = first_q["question_code"]
    engine.asked_question_codes.append(first_q["question_code"])

    # Persist session in MongoDB
    session_data = SessionModel(
        session_id=session_id,
        status=GameStatus.ASKING,
        current_question_code=first_q["question_code"],
        asked_question_codes=engine.asked_question_codes,
        candidate_log_weights=engine.candidate_log_weights,
        question_count=0
    )
    await session_repo.create_session(session_data)
    logger.info(f"Started new game session: {session_id} with question: {first_q['question_code']}")

    return StartGameResponse(
        session_id=session_id,
        status=GameStatus.ASKING,
        question=QuestionDTO(
            question_code=first_q["question_code"],
            text_bn=first_q["text_bn"],
            question_number=1
        )
    )


@router.post("/answer", response_model=AnswerResponse)
async def submit_answer(
    req: AnswerRequest,
    char_repo: CharacterRepository = Depends(get_char_repo),
    q_repo: QuestionRepository = Depends(get_q_repo),
    session_repo: SessionRepository = Depends(get_session_repo),
):
    """Record player's answer, update Bayesian log-scores, and return next question or guess."""
    session_doc = await session_repo.get_active_session(req.session_id)
    if not session_doc:
        raise SessionNotFoundError(req.session_id)

    characters = await char_repo.get_published_characters()
    questions = await q_repo.get_active_questions()

    engine = GameSessionEngine(
        session_id=req.session_id,
        characters=characters,
        questions=questions,
        status=GameStatus(session_doc.get("status", "asking")),
        asked_question_codes=session_doc.get("asked_question_codes", []),
        answer_history=session_doc.get("answer_history", {}),
        candidate_log_weights=session_doc.get("candidate_log_weights", {}),
        rejected_character_ids=session_doc.get("rejected_character_ids", []),
        current_question_code=session_doc.get("current_question_code"),
        question_count=session_doc.get("question_count", 0),
    )

    # Apply Bayesian update
    engine.record_answer(req.question_code, req.answer)

    # Evaluate next move (guess vs next question vs defeat)
    step_result = engine.evaluate_next_step()

    # Persist updated session state
    updates = {
        "status": engine.status.value,
        "current_question_code": engine.current_question_code,
        "asked_question_codes": engine.asked_question_codes,
        "answer_history": engine.answer_history,
        "candidate_log_weights": engine.candidate_log_weights,
        "rejected_character_ids": list(engine.rejected_character_ids),
        "question_count": engine.question_count,
    }
    if step_result.get("guess"):
        updates["proposed_character_id"] = step_result["guess"]["character_id"]

    await session_repo.update_session(req.session_id, updates)

    resp_guess = None
    if step_result.get("guess"):
        g = step_result["guess"]
        resp_guess = CharacterGuessDTO(
            character_id=g["character_id"],
            name_bn=g["name_bn"],
            categories=g["categories"],
            image_url=g["image_url"],
            score=g["score"],
        )

    resp_q = None
    if step_result.get("next_question"):
        nq = step_result["next_question"]
        resp_q = QuestionDTO(
            question_code=nq["question_code"],
            text_bn=nq["text_bn"],
            question_number=nq["question_number"],
        )

    return AnswerResponse(
        status=engine.status,
        next_question=resp_q,
        guess=resp_guess,
    )


@router.post("/guess-feedback", response_model=GuessFeedbackResponse)
async def submit_guess_feedback(
    req: GuessFeedbackRequest,
    char_repo: CharacterRepository = Depends(get_char_repo),
    q_repo: QuestionRepository = Depends(get_q_repo),
    session_repo: SessionRepository = Depends(get_session_repo),
):
    """User confirms whether proposed guess was correct or wrong."""
    session_doc = await session_repo.get_active_session(req.session_id)
    if not session_doc:
        raise SessionNotFoundError(req.session_id)

    proposed_id = session_doc.get("proposed_character_id")
    if not proposed_id:
        raise SessionStateConflictError(
            message="No character guess pending feedback in this session.",
            message_bn="কোনো অনুমান মুলতবি নেই।"
        )

    characters = await char_repo.get_published_characters()
    questions = await q_repo.get_active_questions()

    engine = GameSessionEngine(
        session_id=req.session_id,
        characters=characters,
        questions=questions,
        status=GameStatus(session_doc.get("status", "guess_pending")),
        asked_question_codes=session_doc.get("asked_question_codes", []),
        answer_history=session_doc.get("answer_history", {}),
        candidate_log_weights=session_doc.get("candidate_log_weights", {}),
        rejected_character_ids=session_doc.get("rejected_character_ids", []),
        current_question_code=session_doc.get("current_question_code"),
        question_count=session_doc.get("question_count", 0),
    )

    feedback_result = engine.handle_guess_feedback(req.feedback, proposed_id)

    # If WON, increment character win counter atomically
    if feedback_result["status"] == GameStatus.WON:
        await char_repo.increment_stats(proposed_id, guessed_correctly=True)
    elif feedback_result["status"] == GameStatus.DEFEATED:
        await char_repo.increment_stats(proposed_id, guessed_correctly=False)

    updates = {
        "status": engine.status.value,
        "rejected_character_ids": list(engine.rejected_character_ids),
        "current_question_code": engine.current_question_code,
    }
    await session_repo.update_session(req.session_id, updates)

    resp_q = None
    if feedback_result.get("next_question"):
        nq = feedback_result["next_question"]
        resp_q = QuestionDTO(
            question_code=nq["question_code"],
            text_bn=nq["text_bn"],
            question_number=nq["question_number"],
        )

    return GuessFeedbackResponse(
        status=engine.status,
        message_bn=feedback_result["message_bn"],
        next_question=resp_q,
        guess=None
    )


@router.post("/contributions", response_model=ContributionResponse, status_code=status.HTTP_201_CREATED)
async def submit_contribution(
    req: ContributionRequest,
    session_repo: SessionRepository = Depends(get_session_repo),
    contrib_service: ContributionService = Depends(get_contrib_service),
):
    """User submits a missing character after Genie defeat for moderation review."""
    session_doc = await session_repo.get_active_session(req.session_id)
    if not session_doc:
        raise SessionNotFoundError(req.session_id)

    answer_history = session_doc.get("answer_history", {})

    result = await contrib_service.submit_contribution(
        session_id=req.session_id,
        name_bn=req.name_bn,
        categories=req.categories,
        answer_history=answer_history
    )

    # Mark session finished
    await session_repo.update_session(req.session_id, {"status": GameStatus.FINISHED.value})

    return ContributionResponse(
        status=result["status"],
        contribution_id=result["contribution_id"],
        message_bn=result["message_bn"]
    )


@router.get("/game-state", response_model=GameStateResponse)
async def get_game_state(
    session_id: str,
    q_repo: QuestionRepository = Depends(get_q_repo),
    session_repo: SessionRepository = Depends(get_session_repo),
):
    """Recover current session state for client reconnection or state reload."""
    session_doc = await session_repo.get_active_session(session_id)
    if not session_doc:
        raise SessionNotFoundError(session_id)

    current_q_dto = None
    curr_code = session_doc.get("current_question_code")
    if curr_code:
        q = await q_repo.get_by_code(curr_code)
        if q:
            current_q_dto = QuestionDTO(
                question_code=q["question_code"],
                text_bn=q["text_bn"],
                question_number=session_doc.get("question_count", 0) + 1
            )

    return GameStateResponse(
        session_id=session_id,
        status=GameStatus(session_doc.get("status", "asking")),
        question_count=session_doc.get("question_count", 0),
        current_question=current_q_dto,
        last_guess=None,
        asked_questions_count=len(session_doc.get("asked_question_codes", []))
    )


@router.post("/game/abandon")
async def abandon_game(
    session_id: str,
    session_repo: SessionRepository = Depends(get_session_repo),
):
    """Explicitly abandon and delete an active session."""
    deleted = await session_repo.delete_session(session_id)
    return {"session_id": session_id, "deleted": deleted}
