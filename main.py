import json
import logging
import threading
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
import datetime
import asyncio

from dotenv import dotenv_values
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from starlette.websockets import WebSocket, WebSocketDisconnect

from API.Authentication.jwt_handler import jwt_router
from API.Role_routes.games_role_routes import games_role_router
from API.Role_routes.moves_role_routes import moves_role_router
from API.Role_routes.tournament_role_routes import tournement_role_router
from API.Role_routes.user_role_routes import user_role_router
from API.Role_routes.user_statistics_role_routes import user_statistics_role_router
from API.Routes.leaderboard import leaderboard_router
from API.Routes.profile_routes import profile_router
from API.Routes.role_routes import role_router
from API.Routes.server_stats import server_stats_router
from API.Routes.user_creation_couter_routes import user_creation_router
from API.TwoFactor.TwoFactor import two_factor
from API.Websockets.Rooms import room_manager, Room

from API.Routes.games_routes import games_router
from API.Routes.looking_routes import looking_router
from API.Routes.moves_routes import moves_router
from API.Routes.tournament_registrations_routes import tournament_registrations_router
from API.Routes.tournament_routes import tournament_router
from API.Routes.user_settings_routes import user_settings_router
from API.Routes.user_statistics_routes import user_statistics_router
from API.Routes.user_routes import user_router
from API.Routes.friends_routes import friends_router
from API.Routes.achievement_routes import achievement_router
from datetime import datetime, timezone
from datetime import timedelta

from API.Websockets.notification_manager import notify_router
from API.Websockets.privateroom import private_rooms_router
#from API.Websockets.tournaments import tournament_room_manager


@asynccontextmanager
async def life_span(app: FastAPI) -> AsyncGenerator[None, None]:
    print("----- Server started -----")
    yield
    print("----- Server shutting down... -----")


version = "V1"

app = FastAPI(
    title="CHESS-IT backend",
    description="",
    version=version,
    lifespan=life_span
)

app.include_router(user_router)
app.include_router(role_router)
app.include_router(user_settings_router)
app.include_router(user_statistics_router)
app.include_router(friends_router)
app.include_router(games_router)
app.include_router(moves_router)
app.include_router(looking_router)
app.include_router(tournament_router)
app.include_router(tournament_registrations_router)
app.include_router(profile_router)
app.include_router(user_role_router)
app.include_router(games_role_router)
app.include_router(moves_role_router)
app.include_router(two_factor)
app.include_router(user_statistics_role_router)
app.include_router(tournement_role_router)
app.include_router(leaderboard_router)
app.include_router(server_stats_router)
app.include_router(user_creation_router)
app.include_router(jwt_router)
app.include_router(notify_router)
app.include_router(private_rooms_router)
app.include_router(achievement_router)


RATE_LIMIT = 1000  # Numarul de requesturi permise
RATE_LIMIT_WINDOW = 60  # Perioada de timp in secunde

BAN_THRESHOLD = 5  # Numarul de request-uri pe care un IP poate sa le faca pana ia ban
BAN_DURATION = timedelta(minutes=10)  # durata ban-ului

# Stocarea datelor in temporar ( pana cand serverul este oprit )
request_counts = {}
banned_ips = {}


async def rate_limiter(request: Request, call_next):
    client_ip = request.client.host

    if client_ip in banned_ips:
        raise HTTPException(status_code=403, detail="IP banned")

    if client_ip not in request_counts:
        request_counts[client_ip] = {"count": 1, "timestamp": datetime.now()}
    else:
        if (datetime.now() - request_counts[client_ip]["timestamp"]).total_seconds() > RATE_LIMIT_WINDOW:
            request_counts[client_ip] = {"count": 1, "timestamp": datetime.now()}
        else:
            request_counts[client_ip]["count"] += 1

        if request_counts[client_ip]["count"] > RATE_LIMIT:
            if request_counts[client_ip]["count"] >= BAN_THRESHOLD:
                banned_ips[client_ip] = datetime.now() + BAN_DURATION
                del request_counts[client_ip]
            raise HTTPException(status_code=429, detail="Too many requests")
    # reapelare a middleware-ului
    response = await call_next(request)
    return response


env_vars = dotenv_values(".env")
#origins = env_vars.get("origins")
origins = [
    "http://192.168.0.32:5173",
    "http://localhost:5173",
    "http://25.49.228.147:5173",
    "http://192.168.0.32:5173",
    "https://chessit.netlify.app/login"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(rate_limiter)


async def log_request_time(request, call_next):
    start_time = datetime.now()
    response = await call_next(request)
    end_time = datetime.now()
    response_time = end_time - start_time
    print(f"Endpoint {request.url.path} accessed in {response_time.total_seconds()} seconds")
    return response


app.middleware("http")(log_request_time)


async def cleanup_bans():
    now = datetime.now()
    for ip, ban_end_time in banned_ips.copy().items():
        if now > ban_end_time:
            del banned_ips[ip]


cleanup_interval = 10


async def periodic_cleanup():
    while True:
        await asyncio.sleep(cleanup_interval)
        await cleanup_bans()


'''@app.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str):
    client_jwt = websocket.query_params.get("jwt", "")
    try:
        room = await room_manager.connect(token, websocket, client_jwt)
        print(f"[INFO] Client {token} connected.")
        while True:
            data = await websocket.receive_text()
            await room_manager.broadcast(room, data)
    except ValueError as e:
        print(f"[ERROR] {e}")
        await websocket.close(code=4000)
    except WebSocketDisconnect:
        print(f"[INFO] Client {token} disconnected.")
        room_id = room_manager.client_to_room.get(token)
        if room_id:
            await room_manager.disconnect(token, room_id)
            room = room_manager.rooms.get(room_id)
            if room:
                await room_manager.broadcast(room, f"Client {token} disconnected.")
    except HTTPException as e:
        print(f"[ERROR] {e.detail}")
        await websocket.close(code=e.status_code)
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        await websocket.close(code=4000)'''

logging.basicConfig(level=logging.INFO)


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    try:
        room = await room_manager.connect(client_id, websocket)
        logging.info(f"Client {client_id} connected to room {room.room_id}.")

        try:
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                logging.info(f"Received message from {client_id}: {message}")

                if "jwt_token" in message:
                    room_manager.set_player_jwt(client_id, message["jwt_token"])
                    logging.info(f"Set JWT for {client_id}")

                await room_manager.broadcast(room, message=message)

        except WebSocketDisconnect as e:
            logging.info(f"Client {client_id} disconnected. Code: {e.code}, Reason: {e.reason}")
            await handle_disconnection(client_id, room)

        except Exception as e:
            logging.error(f"Error while receiving message from {client_id}: {e}")
            if room:
                await handle_disconnection(client_id, room)

    except HTTPException as e:
        logging.error(f"Connection rejected for client {client_id}: {e.detail}")
        try:
            await websocket.close(code=4000)
        except Exception as close_error:
            logging.error(f"[DEBUG] Error closing WebSocket during HTTPException: {close_error}")


async def handle_disconnection(client_id: str, room: Room):
    if room:
        await room_manager.disconnect(client_id, room)
        await room_manager.broadcast(room, f"Client {client_id} disconnected.")
        await room_manager.cleanup_original_clients()


async def cleanup_rooms():
    while True:
        print(f"[DEBUG] Running cleanup task at {datetime.now(timezone.utc)}")
        await asyncio.sleep(15)
        expired_rooms = [room_id for room_id, room in room_manager.rooms.items() if room.has_expired()]
        for room_id in expired_rooms:
            print(f"[DEBUG] Cleaning up expired room {room_id}")
            room = room_manager.rooms.pop(room_id, None)
            if room:
                for client_id in list(room.clients.keys()):
                    await room.disconnect(client_id)
            print(f"[DEBUG] Room {room_id} has been cleaned up.")


@app.get("/debug/rooms")
async def debug_rooms():
    return {
        room_id: {
            "clients": list(room.clients.keys()),
            "original_clients": list(room.original_clients),
            "is_full": room.is_full(),
            "has_expired": room.has_expired(),
        }
        for room_id, room in room_manager.rooms.items()
    }


# TODO help requests, report requests on real time, saved on a table (database) and retreived to solve the problems
# TODO notifier (it would function if the user has some important news or his account was banned,warned,muted or other) (or login without the totp code)
# TODO role level restrictions and verify if jwts are valid, pydantic validator for each field

@app.post("/rooms/end")
async def end_client_room(client_id: str = Query(..., description="Client ID of the user requesting to end the room")):
    room = room_manager.get_room_for_client(client_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found for client")

    for other_client_id in list(room.clients.keys()):
        await room.disconnect(other_client_id)

    if room.room_id in room_manager.rooms:
        del room_manager.rooms[room.room_id]

    if client_id in room_manager.active_clients:
        del room_manager.active_clients[client_id]

    if client_id in room_manager.client_to_room:
        del room_manager.client_to_room[client_id]

    return {"detail": "Room has been deleted ( disconnected all clients from room) "}



'''@app.websocket("/ws_tournament/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    try:
        room = tournament_room_manager.get_room_for_client(client_id)
        if room:
            await tournament_room_manager.reconnect(client_id, websocket, room.level)
            logging.info(f"Client {client_id} reconnected to room {room.room_id}.")
        else:
            room = await tournament_room_manager.connect(client_id, websocket, 0)
            logging.info(f"Client {client_id} connected to new room {room.room_id}.")

        try:
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                logging.info(f"Received message from {client_id}: {message}")

                if "jwt_token" in message:
                    tournament_room_manager.set_player_jwt(client_id, message["jwt_token"])
                    logging.info(f"Set JWT for {client_id}")

                await tournament_room_manager.broadcast(room, message=message)

        except WebSocketDisconnect as e:
            logging.info(f"Client {client_id} disconnected. Code: {e.code}, Reason: {e.reason}")
            await tournament_room_manager.disconnect(client_id, room)

        except Exception as e:
            logging.error(f"Error while receiving message from {client_id}: {e}")
            if room:
                await tournament_room_manager.disconnect(client_id, room)

    except HTTPException as e:
        logging.error(f"Connection rejected for client {client_id}: {e.detail}")
        try:
            await websocket.close(code=4000)
        except Exception as close_error:
            logging.error(f"[DEBUG] Error closing WebSocket during HTTPException: {close_error}")

@app.post("/disconnect/{client_id}")
async def disconnect_player(client_id: str):
    room = tournament_room_manager.get_room_for_client(client_id)

    if not room:
        raise HTTPException(status_code=404, detail="Player not found in any room.")

    await tournament_room_manager.disconnect(client_id, room)
    return {"message": f"Player {client_id} has been disconnected from room {room.room_id}"}


@app.get("/tournament/status")
async def get_tournament_status():
    if not tournament_room_manager.started:
        return {"status": "Tournament not started yet."}

    status = {
        "rooms": {
            room_id: {
                "level": room.level,
                "clients": list(room.clients.keys()),
                "is_full": room.is_full(),
                "has_expired": room.has_expired(),
                "winner": room.get_winner(),
                "draw": room.is_draw(),
            }
            for room_id, room in tournament_room_manager.rooms.items()
        },
        "players": tournament_room_manager.scores,
    }

    return status


@app.post("/tournament/finalize")
async def finalize_tournament():
    result = await tournament_room_manager.finalize_tournament()
    return result


@app.post("/update_scores")
async def update_scores(client_id: str, score: float):
    if client_id not in tournament_room_manager.scores:
        raise HTTPException(status_code=404, detail="Player not found.")

    tournament_room_manager.scores[client_id] = score
    return {"message": f"Updated score for player {client_id}: {score}"}


@app.post("/tournament/start")
async def start_tournament():
    tournament_room_manager.start_tournament()
    return {"message": "Tournament has started."}


@app.post("/report-winner/{client_id}")
async def report_winner(client_id: str):
    """Report a winner for a given room."""
    room = tournament_room_manager.get_room_for_client(client_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    room.set_winner(client_id)
    await tournament_room_manager.handle_room_winner(room)
    return {"status": f"Winner {client_id} reported for room {room.room_id}"}


@app.post("/report-draw/{client_id}")
async def report_draw(client_id: str):
    """Report a draw for the current room."""
    room = tournament_room_manager.get_room_for_client(client_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    room.set_draw()
    await tournament_room_manager.handle_draw(room)
    return {"status": f"Draw reported for room {room.room_id}"}


@app.get("/get-scores")
async def get_scores():
    """Retrieve the current player scores."""
    return {"scores": tournament_room_manager.scores}


@app.post("/complete-round/{level}")
async def complete_round(level: int):
    """Complete the current round at a specific level and move winners to the next level."""
    await tournament_room_manager.complete_round(level)
    return {"status": f"Round at level {level} completed"}


@app.post("/pair-players/{level}")
async def pair_players(level: int):
    """Pair players randomly for the next round at a specific level."""
    await tournament_room_manager.pair_players_for_round(level)
    return {"status": f"Players paired for level {level}"}'''

def run_async_tasks():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        tasks = [
            loop.create_task(cleanup_rooms()),
            loop.create_task(periodic_cleanup())
        ]
        loop.run_until_complete(asyncio.gather(*tasks))
    finally:
        loop.close()


if __name__ == "__main__":
    cleanup_thread = threading.Thread(target=run_async_tasks)
    cleanup_thread.start()

    uvicorn.run(app, host="0.0.0.0", port=8000)

"""
user_id: str = Depends(manager)

user = get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="")

pastram ambele deoarece user_id: str = Depends(manager) asigura ca suntem logati si ca in jwt exista un id
celalalt verifica daca user-ul exista in baza de date ( nu a fost sters )

    """
