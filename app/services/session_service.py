from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import Session as SessionModel, Message
from app.schemas import SessionCreate, SessionUpdate
from app.exceptions import NotFoundError


def create_session(db: Session, data: SessionCreate) -> SessionModel:
    session = SessionModel(user_id=data.user_id, title=data.title)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_session(db: Session, session_id: UUID) -> SessionModel:
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise NotFoundError("Session not found")
    return session


def list_sessions(
    db: Session, user_id: str, page: int = 1, page_size: int = 20
) -> tuple[list[SessionModel], int]:
    query = db.query(SessionModel).filter(SessionModel.user_id == user_id)
    total = query.count()
    sessions = (
        query.order_by(SessionModel.updated_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return sessions, total


def get_message_count_for_session(db: Session, session_id: UUID) -> int:
    return db.query(func.count(Message.id)).filter(Message.session_id == session_id).scalar() or 0


def update_session(db: Session, session_id: UUID, data: SessionUpdate) -> SessionModel:
    session = get_session(db, session_id)
    if data.title is not None:
        session.title = data.title
    if data.is_favorite is not None:
        session.is_favorite = data.is_favorite
    db.commit()
    db.refresh(session)
    return session


def delete_session(db: Session, session_id: UUID) -> None:
    session = get_session(db, session_id)
    db.delete(session)
    db.commit()
