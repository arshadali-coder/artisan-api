from pydantic import BaseModel, Field
from typing import List, Optional, Union
from datetime import datetime

# --- Auth & User Schemas ---

class LoginRequest(BaseModel):
    email: Optional[str] = Field(None, example="ram@example.com")
    phone: Optional[str] = Field(None, example="+91 98765 43210")
    username: Optional[str] = None
    password: Optional[str] = Field(None, example="password123")

class RegisterRequest(BaseModel):
    name: str = Field(..., example="Ram Kumar")
    email: Optional[str] = Field(None, example="ram@example.com")
    phone: str = Field(..., example="+91 98765 43210")
    password: Optional[str] = Field(None, example="password123")
    location: Optional[str] = Field("Varanasi, UP", example="Varanasi, UP")
    bio: Optional[str] = Field(None, example="A 3rd generation weaver from Banaras...")
    craftCategory: Optional[str] = Field("Handloom Weaver", example="Handloom Weaver")
    subCraft: Optional[str] = Field("Textiles", example="Textiles")
    avatarUrl: Optional[str] = Field(None, example="https://example.com/avatar.jpg")
    coverUrl: Optional[str] = Field(None, example="https://example.com/cover.jpg")

class ForgotPasswordRequest(BaseModel):
    email: Optional[str] = Field(None, example="ram@example.com")
    phone: Optional[str] = Field(None, example="+91 98765 43210")

class UserProfileData(BaseModel):
    id: str
    name: str
    email: str = "ram@example.com"
    phone: str
    location: str = "Varanasi, UP"
    bio: str = "A 3rd generation weaver from Banaras..."
    craftCategory: str = "Handloom Weaver"
    subCraft: str = "Textiles"
    rating: float = 4.9
    totalProducts: int = 24
    totalSales: int = 150
    avatarUrl: str = "https://example.com/avatar.jpg"
    coverUrl: str = "https://example.com/cover.jpg"

    class Config:
        from_attributes = True

class AuthLoginResponse(BaseModel):
    token: str
    user: UserProfileData

# --- Legacy OTP Schemas ---
class OTPRequest(BaseModel):
    phone_number: str = Field(..., example="+919876543210")

class OTPVerify(BaseModel):
    phone_number: str = Field(..., example="+919876543210")
    otp: str = Field(..., example="123456")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    full_name: str
    phone_number: str

class UserProfileSchema(BaseModel):
    id: str
    phone_number: str
    full_name: str
    role: str
    preferred_language: str
    profile_image_url: Optional[str] = None
    bio: Optional[str] = None
    location_city: Optional[str] = None
    location_state: Optional[str] = None
    craft_type: Optional[str] = None
    bank_account_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True

# --- Product Schemas ---

class ProductItemSchema(BaseModel):
    id: str
    name: str
    description: Optional[str] = ""
    price: float
    stock: int
    sku: str
    category: Optional[str] = ""
    tags: List[str] = []
    imageUrl: str
    soldCount: int = 14
    matchPercentage: int = 92
    marketBenchmark: str = "Similar items sell for ₹550 - ₹700"
    createdAt: str

    class Config:
        from_attributes = True

class ProductListResponse(BaseModel):
    data: List[ProductItemSchema]

class ProductCreateSchema(BaseModel):
    name: Optional[str] = Field(None, example="Wooden Carved Box")
    title: Optional[str] = Field(None, example="Wooden Carved Box")
    description: Optional[str] = Field(None, example="Intricate hand-carved wooden box for jewelry.")
    price: float = Field(..., example=600.0)
    stock: Optional[int] = Field(None, example=3)
    stock_quantity: Optional[int] = Field(None, example=3)
    sku: Optional[str] = Field(None, example="WB-01")
    category: Optional[str] = Field(None, example="Woodcraft")
    tags: List[str] = Field(default=[], example=["Woodcraft", "Handmade", "Storage"])
    imageUrl: Optional[str] = Field(None, example="https://example.com/product1.jpg")
    image_urls: List[str] = Field(default=[])

class ProductStockUpdateSchema(BaseModel):
    stock: Optional[int] = Field(None, example=3)
    stock_quantity: Optional[int] = Field(None, example=3)

class ProductResponseSchema(BaseModel):
    id: str
    artisan_id: str
    sku: str
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = []
    price: float
    ai_suggested_price: Optional[float] = None
    confidence_score: float
    stock_quantity: int
    status: str
    image_urls: List[str] = []
    raw_audio_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class AICatalogResponseSchema(BaseModel):
    title: str
    description: str
    category: str
    tags: List[str]
    suggested_price: float
    market_price_min: float
    market_price_max: float
    match_confidence: int
    transcript_text: str
    uploaded_image_url: str

# --- Order Schemas ---

class OrderItemDetailSchema(BaseModel):
    id: str
    productId: str
    productTitle: str
    quantity: int
    unitPrice: float

class OrderItemResponseSchema(BaseModel):
    id: str
    orderNumber: str
    buyerName: str
    buyerPhone: Optional[str] = None
    shippingCity: str
    shippingState: str
    totalAmount: float
    status: str
    paymentStatus: str
    createdAt: str
    items: List[OrderItemDetailSchema] = []

    class Config:
        from_attributes = True

class OrderListResponse(BaseModel):
    data: List[OrderItemResponseSchema]

class OrderStatusUpdateSchema(BaseModel):
    status: str = Field(..., example="Confirmed")

# --- Media Schemas ---

class MediaUploadResponse(BaseModel):
    status: str = "success"
    filename: str
    url: str
    message: str = "Media uploaded successfully"

# --- Earnings & Storefront Schemas ---
class EarningsSummarySchema(BaseModel):
    total_earnings_this_month: float
    pending_bank_payout: float
    last_payout_amount: float
    last_payout_date: Optional[str] = None
    total_orders_count: int
    pending_orders_count: int

class RequestPayoutSchema(BaseModel):
    amount: float = Field(..., example=5000.0)

class StorefrontProfileSchema(BaseModel):
    artisan: UserProfileData
    rating: float = 4.9
    products_count: int
    total_sales_count: int
    products: List[ProductItemSchema]
