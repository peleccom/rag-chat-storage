from uuid import UUID

from fastapi import APIRouter, Depends, Query, Security
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.dependencies import verify_api_key
from app.schemas import MessageCreate, MessageResponse, PaginatedMessages
from app.services import message_service

router = APIRouter(prefix="/sessions/{session_id}/messages", tags=["Messages"])


@router.post("", response_model=MessageResponse, status_code=201)
def create_message(
    session_id: UUID,
    data: MessageCreate,
    db: DBSession = Depends(get_db),
    _=Security(verify_api_key),
):
    return message_service.create_message(db, session_id, data)


@router.get("", response_model=PaginatedMessages)
def list_messages(
    session_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: DBSession = Depends(get_db),
    _=Security(verify_api_key),
):
    messages, total = message_service.list_messages(db, session_id, page, page_size)
    return PaginatedMessages(
        items=messages,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max(1, (total + page_size - 1) // page_size),
    )
