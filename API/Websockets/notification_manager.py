import json

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, APIRouter
from fastapi.responses import HTMLResponse
from typing import Dict, List

import asyncio


html = """
<!DOCTYPE html>
<html>
<head>
    <title>WebSocket Room Chat with Notifications</title>
    <style>
        body {
            font-family: Arial, sans-serif;
        }
        #notifications {
            margin-top: 20px;
        }
        #notifications ul {
            list-style-type: none;
            padding: 0;
        }
        #notifications li {
            background-color: #f4f4f4;
            margin-bottom: 5px;
            padding: 10px;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <h1>WebSocket Room Chat with Notifications</h1>
    <form id="nameForm" onsubmit="setUsername(event)">
        <input type="text" id="username" placeholder="Enter your name" autocomplete="off" required/>
        <button>Join Chat</button>
    </form>

    <div id="chatRoom" style="display: none;">
        <h2>Chat Room</h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off" required/>
            <button>Send</button>
        </form>
        <ul id='messages'></ul>
    </div>

    <div id="notifications" style="display: none;">
        <h2>Notifications</h2>
        <ul id='notificationMessages'></ul>

        <h3>Send Notification</h3>
        <form onsubmit="sendNotificationToAll(event)">
            <input type="text" id="notifyAllText" placeholder="Notification to all users" autocomplete="off" required/>
            <button>Send to All</button>
        </form>

        <form onsubmit="sendNotificationToUser(event)">
            <input type="text" id="notifyUserText" placeholder="Notification message" autocomplete="off" required/>
            <input type="text" id="notifyUserId" placeholder="Target username" autocomplete="off" required/>
            <button>Send to User</button>
        </form>
    </div>

    <script>
    var ws;
    var notifyWs;
    var username;

    function setUsername(event) {
        event.preventDefault();
        username = document.getElementById('username').value;

        if (username.trim() === "") {
            console.error("Username is required");
            return;
        }

        if (ws) {
            ws.close();  // Close previous chat connection if open
        }

        if (notifyWs) {
            notifyWs.close();  // Close previous notification connection if open
        }

        ws = new WebSocket("ws://localhost:8000/connect-notifier/" + username);
        ws.onopen = function(event) {
            console.log('WebSocket chat connection opened');
            document.getElementById('nameForm').style.display = 'none';
            document.getElementById('chatRoom').style.display = 'block';
        };

        ws.onmessage = function(event) {
            var messages = document.getElementById('messages');
            var message = document.createElement('li');
            var content = document.createTextNode(event.data);
            message.appendChild(content);
            messages.appendChild(message);
        };

        ws.onerror = function(event) {
            console.error('WebSocket chat error:', event);
        };

        ws.onclose = function(event) {
            console.log('WebSocket chat connection closed:', event);
        };

        notifyWs = new WebSocket("ws://localhost:8000/notify/" + username);
        notifyWs.onopen = function(event) {
            console.log('WebSocket notification connection opened');
            document.getElementById('notifications').style.display = 'block';
        };

        notifyWs.onmessage = function(event) {
            var notificationMessages = document.getElementById('notificationMessages');
            var message = document.createElement('li');
            var content = document.createTextNode(event.data);
            message.appendChild(content);
            notificationMessages.appendChild(message);
        };

        notifyWs.onerror = function(event) {
            console.error('WebSocket notification error:', event);
        };

        notifyWs.onclose = function(event) {
            console.log('WebSocket notification connection closed:', event);
        };
    }

    function sendMessage(event) {
        event.preventDefault();
        var input = document.getElementById("messageText");
        if (ws && input.value) {
            ws.send(input.value);
            input.value = '';
        }
    }

    function sendNotificationToAll(event) {
        event.preventDefault();
        var input = document.getElementById("notifyAllText");
        if (notifyWs && input.value) {
            notifyWs.send(JSON.stringify({ type: 'all', message: input.value }));
            input.value = '';
        }
    }

    function sendNotificationToUser(event) {
        event.preventDefault();
        var message = document.getElementById("notifyUserText").value;
        var targetUser = document.getElementById("notifyUserId").value;
        if (notifyWs && message && targetUser) {
            notifyWs.send(JSON.stringify({ type: 'user', message: message, user: targetUser }));
            document.getElementById("notifyUserText").value = '';
            document.getElementById("notifyUserId").value = '';
        }
    }
</script>

</body>
</html>

"""

clients: Dict[str, WebSocket] = {}
notify_router = APIRouter(tags=["Notifier"])

@notify_router.websocket("/connect-notifier/{client_id}")
async def websocket_chat(websocket: WebSocket, client_id: str):
    if client_id in clients:
        await websocket.close(code=4000)
        return
    await websocket.accept()
    clients[client_id] = websocket
    try:
        while True:
            data = await websocket.receive_text()
            for client in clients.values():
                await client.send_text(f"Client {client_id} says: {data}")
    except WebSocketDisconnect:
        del clients[client_id]
        for client in clients.values():
            await client.send_text(f"Client {client_id} disconnected.")


@notify_router.websocket("/notify/{client_id}")
async def websocket_notify(websocket: WebSocket, client_id: str):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            if message['type'] == 'all':
                for client in clients.values():
                    await client.send_text(f"Notification: {message['message']}")
            elif message['type'] == 'user':
                target_client_id = message['user']
                if target_client_id in clients:
                    await clients[target_client_id].send_text(f"Notification from {client_id}: {message['message']}")
    except WebSocketDisconnect:
        pass


class NotificationManager:
    def __init__(self):
        self.connections: Dict[str, WebSocket] = {}

    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        self.connections[client_id] = websocket
        print(f"Client {client_id} connected for notifications.")

    def disconnect(self, client_id: str):
        if client_id in self.connections:
            websocket = self.connections.pop(client_id)
            print(f"Client {client_id} disconnected from notifications.")
            asyncio.create_task(websocket.close())

    async def send_notification(self, target: str, message: str):
        if target in self.connections:
            websocket = self.connections[target]
            await websocket.send_text(message)
        else:
            print(f"Target {target} not connected for notifications.")

    async def broadcast_notification(self, message: str):
        for websocket in self.connections.values():
            await websocket.send_text(message)


notification_manager = NotificationManager()


@notify_router.get("/notifier")
async def get():
    return HTMLResponse(html)


active_notifications: Dict[str, WebSocket] = {}


@notify_router.websocket("/notify/{client_id}")
async def notification_websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    active_notifications[client_id] = websocket
    print(f"Client {client_id} connected for notifications.")

    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received notification data from {client_id}: {data}")
    except WebSocketDisconnect:
        print(f"Client {client_id} disconnected from notifications.")
        del active_notifications[client_id]


async def send_notification_to_all(message: str):
    for websocket in active_notifications.values():
        await websocket.send_text(message)


async def send_notification_to_user(client_id: str, message: str):
    websocket = active_notifications.get(client_id)
    if websocket:
        await websocket.send_text(message)
