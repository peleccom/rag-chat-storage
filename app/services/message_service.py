from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.models import Message, Session as SessionModel
from app.schemas import MessageCreate
from app.exceptions import NotFoundError


def _ensure_session_exists(db: Session, session_id: UUID) -> None:
    exists = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not exists:
        raise NotFoundError("Session not found")


def create_message(db: Session, session_id: UUID, data: MessageCreate) -> Message:
    _ensure_session_exists(db, session_id)
    message = Message(
        session_id=session_id,
        sender=data.sender,
        content=data.content,
        context=data.context,
    )
    db.add(message)
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    session.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(message)
    return message


def list_messages(
    db: Session,
    session_id: UUID,
    page: int = 1,
    page_size: int = 50,
) -> tuple[list[Message], int]:
    _ensure_session_exists(db, session_id)
    query = db.query(Message).filter(Message.session_id == session_id)
    total = query.count()
    messages = (
        query.order_by(Message.created_at.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return messages, total
