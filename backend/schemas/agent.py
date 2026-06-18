from pydantic import BaseModel, field_validator
from typing import List


class AskRequest(BaseModel):
    question: str

    @field_validator("question")
    @classmethod
    def question_must_not_be_whitespace(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Question must not be empty or whitespace-only")
        return v.strip()


class AskResponse(BaseModel):
    answer: str
    sources: List[str]
