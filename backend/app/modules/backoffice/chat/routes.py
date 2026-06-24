# app/modules/backoffice/chat/routes.py
from __future__ import annotations

import uuid
from typing import Dict, Set

from fastapi import (
    APIRouter,
    Depends,
    WebSocket,
    WebSocketDisconnect,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.core.database import get_db

from . import crud
from .schemas import ChatMessageCreate, ChatMessageRead

router = APIRouter(prefix="/backoffice/chat", tags=["Backoffice Chat"])

# ---------------------------------------------------------
# WebSocket Connection Manager (pro Projekt)
# ---------------------------------------------------------
class ConnectionManager:
    def __init__(self) -> None:
        # project_id -> set(WebSocket)
        self.active_connections: Dict[uuid.UUID, Set[WebSocket]] = {}

    async def connect(self, project_id: uuid.UUID, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.setdefault(project_id, set()).add(websocket)

    def disconnect(self, project_id: uuid.UUID, websocket: WebSocket) -> None:
        conns = self.active_connections.get(project_id)
        if not conns:
            return

        conns.discard(websocket)

        if not conns:  # Wenn leer → löschen
            self.active_connections.pop(project_id, None)

    async def broadcast(self, project_id: uuid.UUID, payload: dict) -> None:
        conns = self.active_connections.get(project_id, set())
        dead: list[WebSocket] = []

        for ws in conns:
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)

        # Entfernen toter Verbindungen
        for ws in dead:
            self.disconnect(project_id, ws)


manager = ConnectionManager()


# ---------------------------------------------------------
# REST: Nachrichten verlaufsweise laden
# ---------------------------------------------------------
@router.get(
    "/projects/{project_id}/messages",
    response_model=list[ChatMessageRead],
)
def list_project_messages(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """
    Liefert die letzten Nachrichten eines Projekts
    (pagination unterstützt).
    """
    messages = crud.get_project_messages(
        db=db,
        project_id=project_id,
        limit=limit,
        offset=offset,
    )

    # In v0.1 einfache Ausgabe:
    # DB liefert DESC → wir drehen um, damit vorne alt → hinten neu
    return list(reversed(messages))


# ---------------------------------------------------------
# REST: Neue Nachricht erstellen
# ---------------------------------------------------------
@router.post(
    "/projects/{project_id}/messages",
    response_model=ChatMessageRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_project_message(
    project_id: uuid.UUID,
    payload: ChatMessageCreate,
    db: Session = Depends(get_db),
):
    """
    Erstellt eine neue Nachricht + broadcastet sie live an alle WS-Clients.
    Auth ist in v0.1 stub-only.
    """

    # V0.1: Dummy-Author-Id (bis core.auth existiert)
    # ----------------------------------------------
    # später durch:
    #   current_employee: Employee = Depends(get_current_employee)
    # ersetzen
    dummy_author_id = uuid.UUID("ef8192d3-9334-4256-ab01-a406307ede2a")

    msg = crud.create_message(
        db=db,
        project_id=project_id,
        data=payload,
        author_id=dummy_author_id,
    )

    # WebSocket broadcast
    await manager.broadcast(
        project_id=project_id,
        payload={
            "event": "new_message",
            "data": ChatMessageRead.model_validate(msg).model_dump(),
        },
    )

    return msg


# ---------------------------------------------------------
# WEBSOCKET: Live Chat pro Projekt
# ---------------------------------------------------------
@router.websocket("/ws/projects/{project_id}")
async def project_chat_websocket(
    websocket: WebSocket,
    project_id: uuid.UUID,
):
    """
    Live-Kommunikation für Projekt-Chats.
    v0.1: Keine Auth, nur Echo + Push von REST-Nachrichten.
    """

    await manager.connect(project_id, websocket)

    try:
        while True:
            msg = await websocket.receive_text()

            # Für v0.1: Echo
            await websocket.send_json({
                "event": "pong",
                "raw": msg,
            })

    except WebSocketDisconnect:
        manager.disconnect(project_id, websocket)
    except Exception:
        manager.disconnect(project_id, websocket)
