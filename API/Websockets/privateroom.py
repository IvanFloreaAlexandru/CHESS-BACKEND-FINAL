import uuid
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, APIRouter
from fastapi.responses import HTMLResponse
from typing import Dict, List, Set
from datetime import datetime, timedelta, timezone
import asyncio
from starlette.websockets import WebSocketState

private_rooms_router = APIRouter(tags=["PrivateRooms"])


class PrivateRoom:
    def __init__(self):
        self.room_id = str(uuid.uuid4())
        self.clients: Dict[str, WebSocket] = {}
        self.original_clients: Set[str] = set()
        self.message_buffer: List[dict] = []
        self.creation_time = datetime.now(timezone.utc)
        self.full_time = None
        self.initial_full = False

    def is_empty(self) -> bool:
        return len(self.clients) == 0

    def is_full(self) -> bool:
        if len(self.clients) >= 2 or len(self.original_clients) == 2:
            if not self.initial_full:
                self.full_time = datetime.now(timezone.utc)
                self.initial_full = True
                print(f"[DEBUG] Room {self.room_id} is now full for the first time.")

                if len(self.original_clients) >= 2:
                    client_ids = list(self.original_clients)
                    white_player_id = client_ids[0]
                    black_player_id = client_ids[1]

                    white_player_jwt = self.get_jwt_for_player(white_player_id)
                    black_player_jwt = self.get_jwt_for_player(black_player_id)

                    message = {
                        "white_player_jwt": white_player_jwt,
                        "black_player_jwt": black_player_jwt
                    }
                    asyncio.create_task(self.broadcast(message))
            return True
        return False

    def get_jwt_for_player(self, player_id: str) -> str:
        jwt_token = private_room_manager.get_player_jwt(player_id)
        return jwt_token

    def has_expired(self) -> bool:
        if self.full_time is None:
            return False
        expired = datetime.now(timezone.utc) > self.full_time + timedelta(minutes=2)
        return expired

    async def broadcast(self, message: dict):
        self.message_buffer.append(message)
        for websocket in list(self.clients.values()):
            if websocket.application_state == WebSocketState.CONNECTED:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    print(f"[DEBUG] Error sending message: {e}")

    async def disconnect(self, client_id: str):
        if client_id in self.clients:
            websocket = self.clients.pop(client_id)
            try:
                if websocket.application_state == WebSocketState.CONNECTED:
                    await websocket.close()
            except Exception as e:
                print(f"[DEBUG] Error closing WebSocket {client_id}: {e}")

    async def connect(self, client_id: str, websocket: WebSocket):
        if client_id in self.clients:
            raise HTTPException(status_code=400, detail=f"Client ID '{client_id}' is already in this room.")

        await websocket.accept()
        self.clients[client_id] = websocket
        self.original_clients.add(client_id)
        for message in self.message_buffer:
            try:
                await websocket.send_json(message)
            except Exception as e:
                print(f"[DEBUG] Error sending buffered message: {e}")
        self.is_full()


class PrivateRoomManager:
    def __init__(self):
        self.rooms: Dict[str, PrivateRoom] = {}
        self.client_to_room: Dict[str, str] = {}
        self.active_clients: Dict[str, WebSocket] = {}
        self.player_jwt_tokens: Dict[str, str] = {}

    def set_player_jwt(self, client_id: str, jwt_token: str):
        self.player_jwt_tokens[client_id] = jwt_token

    def get_player_jwt(self, client_id: str) -> str:
        return self.player_jwt_tokens.get(client_id, "")

    def get_room_for_client(self, client_id: str) -> PrivateRoom:
        room_id = self.client_to_room.get(client_id)
        if room_id:
            return self.rooms.get(room_id)
        return None

    def get_available_room(self) -> PrivateRoom:
        for room_id, room in list(self.rooms.items()):
            if room.has_expired():
                for client_id in list(room.clients.keys()):
                    asyncio.create_task(room.disconnect(client_id))
                del self.rooms[room_id]
            elif not room.is_full():
                return room

        new_room = PrivateRoom()
        self.rooms[new_room.room_id] = new_room
        return new_room

    async def connect(self, client_id: str, websocket: WebSocket, room_id: str = None) -> PrivateRoom:
        if client_id in self.active_clients:
            raise HTTPException(status_code=400, detail=f"Client ID '{client_id}' is already connected.")

        room = None
        if room_id:
            room = self.rooms.get(room_id)
            if not room:
                raise HTTPException(status_code=404, detail=f"Room ID '{room_id}' not found.")
        else:
            room = self.get_available_room()

        if room.is_full() and client_id not in room.original_clients:
            raise HTTPException(status_code=400, detail=f"Room {room.room_id} is full and does not accept new clients.")

        self.active_clients[client_id] = websocket
        self.client_to_room[client_id] = room.room_id
        await room.connect(client_id, websocket)
        return room

    async def disconnect(self, client_id: str, room: PrivateRoom):
        if room is not None:
            await room.disconnect(client_id)
            if room.is_empty():
                room_id = room.room_id
                if room_id in self.rooms:
                    del self.rooms[room_id]
        if client_id in self.active_clients:
            del self.active_clients[client_id]
        if client_id in self.client_to_room:
            del self.client_to_room[client_id]

    async def broadcast(self, room: PrivateRoom, message: dict):
        await room.broadcast(message)

    async def cleanup_original_clients(self):
        for room in list(self.rooms.values()):
            if room.has_expired():
                for client_id in list(room.original_clients):
                    if client_id in self.active_clients:
                        continue
                    room.original_clients.discard(client_id)

    def get_total_active_users(self) -> int:
        active_users_count = 0
        for room in self.rooms.values():
            active_users_count += len(room.clients)
        return active_users_count


private_room_manager = PrivateRoomManager()


@private_rooms_router.websocket("/room/{room_id}/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, client_id: str):
    room = private_room_manager.get_room_for_client(client_id)
    if room:
        await private_room_manager.disconnect(client_id, room)
    room = await private_room_manager.connect(client_id, websocket, room_id)

    try:
        while True:
            data = await websocket.receive_text()
            await private_room_manager.broadcast(room, {"user": client_id, "message": data})
    except WebSocketDisconnect:
        await private_room_manager.disconnect(client_id, room)


@private_rooms_router.get("/rooms/{room_id}")
async def get_room(room_id: str):
    room = private_room_manager.rooms.get(room_id)
    if room:
        return {"room_id": room.room_id, "clients": list(room.clients.keys())}
    else:
        raise HTTPException(status_code=404, detail="Room not found.")


@private_rooms_router.get("/create-room/")
async def create_room():
    room = PrivateRoom()
    private_room_manager.rooms[room.room_id] = room
    return {"room_id": room.room_id}


@private_rooms_router.get("/private_room")
async def get():
    return HTMLResponse(html)


html = """
<!DOCTYPE html>
<html>
<head>
    <title>Private Room Chat</title>
    <style>
        body {
            font-family: Arial, sans-serif;
        }
        #chat {
            margin-top: 20px;
        }
        #messages {
            list-style-type: none;
            padding: 0;
        }
        #messages li {
            background-color: #f4f4f4;
            margin-bottom: 5px;
            padding: 10px;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <h1>Private Room Chat</h1>
    <form id="roomForm" onsubmit="joinRoom(event)">
        <input type="text" id="roomId" placeholder="Enter Room UUID" required>
        <input type="text" id="clientId" placeholder="Enter Your Client ID" required>
        <button type="submit">Join Room</button>
    </form>
    <div id="chat">
        <h2>Chat Messages</h2>
        <ul id="messages"></ul>
        <input type="text" id="messageInput" placeholder="Type a message..." onkeydown="if(event.key === 'Enter') sendMessage()">
    </div>
    <script>
        let ws;

        function joinRoom(event) {
            event.preventDefault();
            const roomId = document.getElementById('roomId').value;
            const clientId = document.getElementById('clientId').value;

            if (ws) {
                ws.close();
            }

            ws = new WebSocket(`ws://localhost:8000/room/${roomId}/ws/${clientId}`);

            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                if (data.message) {
                    const messagesList = document.getElementById('messages');
                    const messageItem = document.createElement('li');
                    messageItem.textContent = `${data.user}: ${data.message}`;
                    messagesList.appendChild(messageItem);
                }
            };

            ws.onopen = function() {
                const messagesList = document.getElementById('messages');
                messagesList.innerHTML = '';  // Clear previous messages
            };

            ws.onclose = function() {
                const messagesList = document.getElementById('messages');
                const messageItem = document.createElement('li');
                messageItem.textContent = 'Disconnected from room.';
                messagesList.appendChild(messageItem);
            };
        }

        function sendMessage() {
            const messageInput = document.getElementById('messageInput');
            if (ws && messageInput.value.trim()) {
                ws.send(messageInput.value);
                messageInput.value = '';
            }
        }
    </script>
</body>
</html>
"""
