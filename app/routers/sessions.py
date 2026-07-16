from uuid import UUID

from fastapi import APIRouter, Depends, Query, Security
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.dependencies import verify_api_key
from app.schemas import SessionCreate, SessionUpdate, SessionResponse
from app.services import session_service

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.post("", response_model=SessionResponse, status_code=201)
def create_session(
    data: SessionCreate,
    db: DBSession = Depends(get_db),
    _=Security(verify_api_key),
):
    session = session_service.create_session(db, data)
    return _enrich_session(db, session)


@router.get("", response_model=dict)
def list_sessions(
    user_id: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: DBSession = Depends(get_db),
    _=Security(verify_api_key),
):
    sessions, total = session_service.list_sessions(db, user_id, page, page_size)
    enriched = [_enrich_session(db, s) for s in sessions]
    return {
        "items": enriched,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, (total + page_size - 1) // page_size),
    }


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(
    session_id: UUID,
    db: DBSession = Depends(get_db),
    _=Security(verify_api_key),
):
    session = session_service.get_session(db, session_id)
    return _enrich_session(db, session)


@router.patch("/{session_id}", response_model=SessionResponse)
def update_session(
    session_id: UUID,
    data: SessionUpdate,
    db: DBSession = Depends(get_db),
    _=Security(verify_api_key),
):
    session = session_service.update_session(db, session_id, data)
    return _enrich_session(db, session)


@router.delete("/{session_id}", status_code=204)
def delete_session(
    session_id: UUID,
    db: DBSession = Depends(get_db),
    _=Security(verify_api_key),
):
    session_service.delete_session(db, session_id)


def _enrich_session(db: DBSession, session) -> SessionResponse:
    count = session_service.get_message_count_for_session(db, session.id)
    return SessionResponse(
        id=session.id,
        user_id=session.user_id,
        title=session.title,
        is_favorite=session.is_favorite,
        created_at=session.created_at,
        updated_at=session.updated_at,
        message_count=count,
    )
