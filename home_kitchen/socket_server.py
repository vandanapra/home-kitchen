import socketio

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*"
)

app = socketio.ASGIApp(sio)

@sio.event
async def connect(sid, environ):
    print("🔌 Client connected:", sid)

@sio.event
async def join_seller(sid, seller_id):
    await sio.enter_room(sid, f"seller_{seller_id}")
    print(f"Seller {seller_id} joined room")

async def notify_seller(seller_id, data):
    await sio.emit(
        "new_order",
        data,
        room=f"seller_{seller_id}"
    )
