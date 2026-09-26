# 🏺 Artisan Market App — FastAPI Specification & Backend

Production-grade FastAPI backend and database system built for the **Artisan Market App** and Flutter Web frontends.

---

## ⚙️ 1. Global Configuration

| Setting | Configuration / Value |
| :--- | :--- |
| **Local Development** | `http://<YOUR_LAN_IP>:8000` or `http://127.0.0.1:8000` |
| **Production** | `https://<YOUR_API_DOMAIN>.com` |
| **Authentication** | OAuth2 with Bearer Tokens (`Authorization: Bearer <token>`) |
| **CORS** | Configured for Flutter Web, Mobile Apps, and cross-origin requests (`allow_origins=["*"]`) |

---

## 🔑 2. Authentication Endpoints (`/auth`)

| Method | Route | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/auth/login` | Authenticates user and returns session token alongside artisan profile data. | ❌ |
| `POST` | `/auth/register` | Creates a new artisan account. | ❌ |
| `POST` | `/auth/forgot-password` | Initiates password recovery flow (sends OTP or reset link). | ❌ |
| `POST` | `/auth/logout` | Invalidates current Bearer token session. | ✅ |

### 📄 Expected JSON Response (`POST /auth/login` & `POST /auth/register`):
```json
{
  "token": "eyJhbGciOi...",
  "user": {
    "id": "u_001",
    "name": "Ram Kumar",
    "email": "ram@example.com",
    "phone": "+91 98765 43210",
    "location": "Varanasi, UP",
    "bio": "A 3rd generation weaver from Banaras...",
    "craftCategory": "Handloom Weaver",
    "subCraft": "Textiles",
    "rating": 4.9,
    "totalProducts": 24,
    "totalSales": 150,
    "avatarUrl": "https://example.com/avatar.jpg",
    "coverUrl": "https://example.com/cover.jpg"
  }
}
```

---

## 📦 3. Product & Inventory Endpoints (`/products`)

| Method | Route | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/products` | Retrieves the list of products for the authenticated artisan. | ✅ |
| `POST` | `/products` | Creates and publishes a new product to the catalog. | ✅ |
| `POST` | `/products/{id}/stock` | Adjusts the inventory count for a specific product ID. | ✅ |

### 📄 Expected JSON Response (`GET /products`):
```json
{
  "data": [
    {
      "id": "prod_001",
      "name": "Wooden Carved Box",
      "description": "Intricate hand-carved wooden box for jewelry.",
      "price": 600.0,
      "stock": 3,
      "sku": "WB-01",
      "category": "Woodcraft",
      "tags": ["Woodcraft", "Handmade", "Storage"],
      "imageUrl": "https://example.com/product1.jpg",
      "soldCount": 14,
      "matchPercentage": 92,
      "marketBenchmark": "Similar items sell for ₹550 - ₹700",
      "createdAt": "2024-01-01T00:00:00.000Z"
    }
  ]
}
```

---

## 🛒 4. Order Management Endpoints (`/orders`)

| Method | Route | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/orders` | Retrieves list of orders (Pending, Processing, Shipped, Delivered). | ✅ |
| `PATCH` | `/orders/{id}` | Updates status of a specific order ID (e.g., Pending to Confirmed). | ✅ |

---

## 🎙️ 5. Media Endpoints (`/media`)

| Method | Route | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/media/upload` | Accepts multi-part form data (images/audio) and returns hosted file URL. | ❌ / ✅ |

### 📄 Expected JSON Response (`POST /media/upload`):
```json
{
  "status": "success",
  "filename": "uploaded_image_123.jpg",
  "url": "http://127.0.0.1:8000/static/uploads/uploaded_image_123.jpg",
  "message": "Media uploaded successfully"
}
```

---

## 🚀 Quickstart Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the FastAPI Development Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The server will launch on your local machine and LAN IP at `http://<YOUR_LAN_IP>:8000`.

### 3. Interactive API Documentation
* **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **ReDoc UI**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
