from typing import List, Optional

from pydantic import BaseModel, field_validator


class AskRequest(BaseModel):
    question: str
    # Optional conversation identifier.  When provided, the in-memory
    # checkpointer retains messages for this thread across requests.
    # When absent (default), the graph runs statelessly.
    thread_id: Optional[str] = None

    @field_validator("question")
    @classmethod
    def question_must_not_be_whitespace(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Question must not be empty or whitespace-only")
        return v.strip()


class AskResponse(BaseModel):
    answer: str
    sources: List[str]
