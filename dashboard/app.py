"""FastAPI + WebSocket dashboard server."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="Sangha Dashboard")

_STATIC = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(_STATIC)), name="static")

_connections: list[WebSocket] = []


class ConfigRequest(BaseModel):
    yaml: str
    config: dict


@app.get("/")
async def index():
    return FileResponse(_STATIC / "index.html")


@app.post("/api/save-config")
async def save_config(req: ConfigRequest):
    """Save configuration to settings.yaml"""
    try:
        config_path = Path("config/settings.yaml")
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(req.yaml)
        return JSONResponse({"status": "success", "message": "Configuration saved"})
    except Exception as e:
        return JSONResponse(
            {"status": "error", "message": str(e)}, status_code=500
        )


@app.get("/api/config")
async def get_config():
    """Get current configuration"""
    try:
        config_path = Path("config/settings.yaml")
        if config_path.exists():
            content = config_path.read_text()
            return JSONResponse({"status": "success", "yaml": content})
        return JSONResponse(
            {"status": "error", "message": "Config file not found"}, status_code=404
        )
    except Exception as e:
        return JSONResponse(
            {"status": "error", "message": str(e)}, status_code=500
        )


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
