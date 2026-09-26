import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import engine, Base, run_migrations
from app.routers import auth, products, orders, earnings, public, media
from app.websockets.manager import ws_manager

# Auto-migrate SQLite database columns if missing
run_migrations()

# Create database tables automatically on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="FastAPI Backend for Artisan Market App - Full API Specification",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for Flutter Web, mobile apps, and cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins for local LAN IP & Flutter web apps
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure static upload directory exists and mount static routes
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount Routers at root (for spec endpoints: /auth, /products, /orders, /media)
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(media.router)
app.include_router(earnings.router)
app.include_router(public.router)

# Also mount Routers under API_PREFIX (/api/v1) for backward compatibility
app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(products.router, prefix=settings.API_PREFIX)
app.include_router(orders.router, prefix=settings.API_PREFIX)
app.include_router(media.router, prefix=settings.API_PREFIX)
app.include_router(earnings.router, prefix=settings.API_PREFIX)
app.include_router(public.router, prefix=settings.API_PREFIX)

@app.get("/")
def root():
    return {
        "status": "online",
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "auth": ["/auth/login", "/auth/register", "/auth/forgot-password", "/auth/logout"],
            "products": ["GET /products", "POST /products", "POST /products/{id}/stock"],
            "orders": ["GET /orders", "PATCH /orders/{id}"],
            "media": ["POST /media/upload"]
        }
    }

# WebSocket Endpoint for Real-time Order Notifications
@app.websocket("/ws/orders/{user_id}")
async def websocket_orders_endpoint(websocket: WebSocket, user_id: str):
    await ws_manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_json({"event": "PONG", "payload": data})
    except WebSocketDisconnect:
        ws_manager.disconnect(user_id, websocket)
