from sqlalchemy.orm import Session
from ..db.database import InterviewSession, InterviewLog
import uuid

class SessionManager:
    def __init__(self, db: Session):
        self.db = db

    def create_session(self, company: str, position: str, difficulty: str, question_limit: int):
        session_id = str(uuid.uuid4())
        new_session = InterviewSession(
            id=session_id,
            company=company,
            position=position,
            difficulty=difficulty,
            question_limit=question_limit,
            history=""
        )
        self.db.add(new_session)
        self.db.commit()
        return new_session

    def get_session(self, session_id: str):
        return self.db.query(InterviewSession).filter(InterviewSession.id == session_id).first()

    def update_history(self, session_id: str, text: str):
        session = self.get_session(session_id)
        if session:
            session.history += text
            self.db.commit()
        return session

    def log_turn(self, session_id: str, question: str, answer: str, evaluation):
        log = InterviewLog(
            session_id=session_id,
            question=question,
            answer=answer,
            technical_score=evaluation.technical_score,
            clarity_score=evaluation.clarity_score,
            structure_score=evaluation.structure_score,
            confidence_score=evaluation.confidence_score,
            strengths=evaluation.strengths,
            weaknesses=evaluation.weaknesses,
            improvement_plan=evaluation.improvement_plan
        )
        self.db.add(log)
        self.db.commit()
        return log

    def get_logs(self, session_id: str):
        return self.db.query(InterviewLog).filter(InterviewLog.session_id == session_id).all()
