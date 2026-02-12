from pydantic import BaseModel
from typing import List, Optional

class Evaluation(BaseModel):
    technical_score: int
    clarity_score: int
    structure_score: int
    confidence_score: int
    professionalism_score: int
    strengths: str
    weaknesses: str
    improvement_plan: str

class FinalEvaluation(BaseModel):
    total_score: int
    hiring_chances: str
    summary: str

class InterviewStart(BaseModel):
    company: Optional[str] = "General"
    position: Optional[str] = "Software Engineer"
    difficulty: Optional[str] = "Intermediate"
    question_limit: Optional[int] = 5

class InterviewSession(BaseModel):
    session_id: str
    current_question: str

class UserAnswer(BaseModel):
    session_id: str
    answer_text: str
