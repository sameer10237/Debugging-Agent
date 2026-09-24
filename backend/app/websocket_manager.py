"""WebSocket support for real-time execution updates."""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Set, Dict, Any, Optional
import json
import logging
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class MessageType(str, Enum):
    """WebSocket message types."""
    STATUS_UPDATE = "status_update"
    AGENT_UPDATE = "agent_update"
    ANALYSIS_COMPLETE = "analysis_complete"
    ERROR = "error"
    LOG = "log"


class WebSocketManager:
    """Manage WebSocket connections for real-time updates."""

    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.execution_streams: Dict[str, list] = {}

    async def connect(self, execution_id: str, websocket: WebSocket):
        """Accept and register a WebSocket connection."""
        await websocket.accept()
        
        if execution_id not in self.active_connections:
            self.active_connections[execution_id] = set()
            self.execution_streams[execution_id] = []
        
        self.active_connections[execution_id].add(websocket)
        logger.info(f"WebSocket connected for execution {execution_id}")

    def disconnect(self, execution_id: str, websocket: WebSocket):
        """Remove a disconnected WebSocket."""
        if execution_id in self.active_connections:
            self.active_connections[execution_id].discard(websocket)
            if not self.active_connections[execution_id]:
                del self.active_connections[execution_id]
                if execution_id in self.execution_streams:
                    del self.execution_streams[execution_id]

    async def broadcast_status(
        self,
        execution_id: str,
        agent_name: str,
        status: str,
        data: Optional[Dict[str, Any]] = None
    ):
        """Broadcast agent status update to all connected clients."""
        if execution_id not in self.active_connections:
            return

        message = {
            "type": MessageType.AGENT_UPDATE,
            "execution_id": execution_id,
            "agent": agent_name,
            "status": status,
            "data": data or {},
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Store in stream
        self.execution_streams[execution_id].append(message)

        # Send to all connected clients
        disconnected = set()
        for websocket in self.active_connections[execution_id]:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending WebSocket message: {str(e)}")
                disconnected.add(websocket)

        # Clean up disconnected clients
        for ws in disconnected:
            self.disconnect(execution_id, ws)

    async def broadcast_analysis_complete(
        self,
        execution_id: str,
        results: Dict[str, Any]
    ):
        """Broadcast analysis completion."""
        if execution_id not in self.active_connections:
            return

        message = {
            "type": MessageType.ANALYSIS_COMPLETE,
            "execution_id": execution_id,
            "results": results,
            "timestamp": datetime.utcnow().isoformat(),
        }

        for websocket in self.active_connections[execution_id]:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending completion: {str(e)}")

    async def broadcast_error(
        self,
        execution_id: str,
        error: str,
        agent: Optional[str] = None
    ):
        """Broadcast error message."""
        if execution_id not in self.active_connections:
            return

        message = {
            "type": MessageType.ERROR,
            "execution_id": execution_id,
            "error": error,
            "agent": agent,
            "timestamp": datetime.utcnow().isoformat(),
        }

        for websocket in self.active_connections[execution_id]:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending error message: {str(e)}")

    def get_stream(self, execution_id: str) -> list:
        """Get the message stream for an execution."""
        return self.execution_streams.get(execution_id, [])


# Global WebSocket manager
_ws_manager: Optional[WebSocketManager] = None


def get_ws_manager() -> WebSocketManager:
    """Get or create WebSocket manager."""
    global _ws_manager
    if _ws_manager is None:
        _ws_manager = WebSocketManager()
    return _ws_manager
