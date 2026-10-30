"""Domain models, enumerations, and mathematical likelihood mapping."""

from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class AnswerEnum(str, Enum):
    """User answer options."""
    YES = "YES"
    PROBABLY_YES = "PROBABLY_YES"
    UNKNOWN = "UNKNOWN"
    PROBABLY_NO = "PROBABLY_NO"
    NO = "NO"


class GameStatus(str, Enum):
    """Finite state machine states."""
    READY = "ready"
    ASKING = "asking"
    GUESS_PENDING = "guess_pending"
    WON = "won"
    DEFEATED = "defeated"
    CONTRIBUTION_PENDING = "contribution_pending"
    FINISHED = "finished"


class FeedbackEnum(str, Enum):
    """User feedback on Genie's proposed guess."""
    CORRECT = "correct"
    WRONG = "wrong"


# Categorical Likelihood Model: P(user_answer | character_fact)
# Each condition (True, False, None) sums strictly to 1.0 across all 5 user answers.
LIKELIHOOD_TABLE: Dict[tuple, float] = {
    # If character attribute is TRUE (sum = 1.00)
    (True, AnswerEnum.YES): 0.65,
    (True, AnswerEnum.PROBABLY_YES): 0.20,
    (True, AnswerEnum.UNKNOWN): 0.08,
    (True, AnswerEnum.PROBABLY_NO): 0.05,
    (True, AnswerEnum.NO): 0.02,

    # If character attribute is FALSE (sum = 1.00)
    (False, AnswerEnum.YES): 0.02,
    (False, AnswerEnum.PROBABLY_YES): 0.05,
    (False, AnswerEnum.UNKNOWN): 0.08,
    (False, AnswerEnum.PROBABLY_NO): 0.20,
    (False, AnswerEnum.NO): 0.65,

    # If character attribute is UNKNOWN/NEUTRAL (sum = 1.00)
    (None, AnswerEnum.YES): 0.15,
    (None, AnswerEnum.PROBABLY_YES): 0.15,
    (None, AnswerEnum.UNKNOWN): 0.40,
    (None, AnswerEnum.PROBABLY_NO): 0.15,
    (None, AnswerEnum.NO): 0.15,
}


class FactRecord(BaseModel):
    """Individual character answer fact with confidence and source."""
    value: bool
    confidence: float = 1.0
    source: str = "editor_verified"


class QuestionModel(BaseModel):
    """Domain model for a question."""
    id: Optional[str] = None
    question_code: str
    text_bn: str
    text_en: Optional[str] = None
    answer_type: str = "boolean"
    active: bool = True
    order: int = 10
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CharacterModel(BaseModel):
    """Domain model for a character."""
    id: Optional[str] = None
    name_bn: str
    name_en: Optional[str] = None
    normalized_name: str
    aliases_bn: List[str] = Field(default_factory=list)
    aliases_en: List[str] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)
    is_real_person: bool = True
    is_alive: bool = True
    answer_profile: Dict[str, FactRecord] = Field(default_factory=dict)
    image_url: Optional[str] = None
    image_attribution: Optional[str] = None
    status: str = "published"  # published, pending_review, rejected
    times_played: int = 0
    times_guessed_correctly: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class SessionModel(BaseModel):
    """Domain model for a persisted game session."""
    id: Optional[str] = None
    session_id: str
    status: GameStatus = GameStatus.ASKING
    current_question_code: Optional[str] = None
    asked_question_codes: List[str] = Field(default_factory=list)
    answer_history: Dict[str, AnswerEnum] = Field(default_factory=dict)
    candidate_log_weights: Dict[str, float] = Field(default_factory=dict)
    rejected_character_ids: List[str] = Field(default_factory=list)
    proposed_character_id: Optional[str] = None
    question_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None


class ContributionModel(BaseModel):
    """Community contribution record."""
    id: Optional[str] = None
    session_id: str
    name_bn: str
    normalized_name: str
    categories: List[str] = Field(default_factory=list)
    answer_history: Dict[str, AnswerEnum] = Field(default_factory=dict)
    status: str = "pending_review"
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
