"""FastAPI + WebSocket dashboard server."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Sangha Dashboard")

_STATIC = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(_STATIC)), name="static")

_connections: list[WebSocket] = []


@app.get("/")
async def index():
    return FileResponse(_STATIC / "index.html")


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    _connections.append(ws)
    try:
        while True:
            await ws.receive_text()  # keep-alive ping
    except WebSocketDisconnect:
        _connections.remove(ws)


async def broadcast(data: dict) -> None:
    """Broadcast a message to all connected dashboard clients."""
    msg = json.dumps(data)
    dead: list[WebSocket] = []
    for ws in _connections:
        try:
            await ws.send_text(msg)
        except Exception:
            dead.append(ws)
    for ws in dead:
        _connections.remove(ws)
