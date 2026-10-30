"""Pydantic API request and response validation schemas."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.models.domain import AnswerEnum, GameStatus, FeedbackEnum


class QuestionDTO(BaseModel):
    """Question representation sent to client."""
    question_code: str
    text_bn: str
    question_number: int


class CharacterGuessDTO(BaseModel):
    """Character guess presented to client."""
    character_id: str
    name_bn: str
    categories: List[str]
    image_url: Optional[str] = None
    score: float


# 1. Start Game
class StartGameResponse(BaseModel):
    session_id: str
    status: GameStatus
    question: QuestionDTO


# 2. Answer Question
class AnswerRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    question_code: str = Field(..., min_length=1)
    answer: AnswerEnum


class AnswerResponse(BaseModel):
    status: GameStatus
    next_question: Optional[QuestionDTO] = None
    guess: Optional[CharacterGuessDTO] = None


# 3. Guess Feedback
class GuessFeedbackRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    feedback: FeedbackEnum


class GuessFeedbackResponse(BaseModel):
    status: GameStatus
    message_bn: str
    next_question: Optional[QuestionDTO] = None
    guess: Optional[CharacterGuessDTO] = None


# 4. Contribution
class ContributionRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    name_bn: str = Field(..., min_length=2, max_length=100)
    categories: List[str] = Field(..., min_length=1, max_length=5)


class ContributionResponse(BaseModel):
    status: str
    contribution_id: str
    message_bn: str


# 5. Session State Recovery
class GameStateResponse(BaseModel):
    session_id: str
    status: GameStatus
    question_count: int
    current_question: Optional[QuestionDTO] = None
    last_guess: Optional[CharacterGuessDTO] = None
    asked_questions_count: int
