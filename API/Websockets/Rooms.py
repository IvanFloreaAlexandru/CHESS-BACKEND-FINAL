import uuid
from fastapi import WebSocket, HTTPException
from typing import Dict, List, Set
from datetime import datetime, timedelta, timezone
import asyncio
from starlette.websockets import WebSocketState


class Room:
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

                    print(f"[DEBUG] White player ID: {white_player_id}")
                    print(f"[DEBUG] Black player ID: {black_player_id}")
                    print(f"[DEBUG] White player JWT: {white_player_jwt}")
                    print(f"[DEBUG] Black player JWT: {black_player_jwt}")

                    message = {
                        "white_player_jwt": white_player_id,
                        "black_player_jwt": black_player_id
                    }
                    asyncio.create_task(self.broadcast(message))
                else:
                    print("[DEBUG] Not enough clients to set JWTs.")
            return True
        return False

    def get_jwt_for_player(self, player_id: str) -> str:
        jwt_token = room_manager.get_player_jwt(player_id)
        print(f"[DEBUG] Get JWT for {player_id}: {jwt_token}")
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
                else:
                    print(f"[DEBUG] WebSocket {client_id} is already in state {websocket.application_state}.")
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


class RoomManager:
    def __init__(self):
        self.rooms: Dict[str, Room] = {}
        self.client_to_room: Dict[str, str] = {}
        self.active_clients: Dict[str, WebSocket] = {}
        self.player_jwt_tokens: Dict[str, str] = {}

    def set_player_jwt(self, client_id: str, jwt_token: str):
        self.player_jwt_tokens[client_id] = jwt_token
        print(f"[DEBUG] Set JWT for {client_id}: {jwt_token}")

    def get_player_jwt(self, client_id: str) -> str:
        jwt_token = self.player_jwt_tokens.get(client_id, "")
        print(f"[DEBUG] Get JWT for {client_id}: {jwt_token}")
        return jwt_token

    def get_room_for_client(self, client_id: str) -> Room:
        room_id = self.client_to_room.get(client_id)
        if room_id:
            return self.rooms.get(room_id)
        return None

    def get_available_room(self) -> Room:
        for room_id, room in list(self.rooms.items()):
            if room.has_expired():
                for client_id in list(room.clients.keys()):
                    asyncio.create_task(room.disconnect(client_id))
                del self.rooms[room_id]
            elif not room.is_full():
                return room

        new_room = Room()
        self.rooms[new_room.room_id] = new_room
        return new_room

    async def connect(self, client_id: str, websocket: WebSocket) -> Room:
        if client_id in self.active_clients:
            raise HTTPException(status_code=400, detail=f"Client ID '{client_id}' is already connected.")

        room_to_connect = None
        for room in self.rooms.values():
            if client_id in room.original_clients:
                room_to_connect = room
                break

        if room_to_connect:
            room = room_to_connect
        else:
            room = self.get_available_room()

        if room.is_full() and client_id not in room.original_clients:
            raise HTTPException(status_code=400, detail=f"Room {room.room_id} is full and does not accept new clients.")

        self.active_clients[client_id] = websocket
        self.client_to_room[client_id] = room.room_id
        await room.connect(client_id, websocket)
        return room

    async def disconnect(self, client_id: str, room: Room):
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

    async def broadcast(self, room: Room, message: dict):
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


room_manager = RoomManager()
