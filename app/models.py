import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    phone_number = Column(String(30), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=True)
    full_name = Column(String(100), nullable=False)
    role = Column(String(20), default="ARTISAN") # ARTISAN or BUYER
    preferred_language = Column(String(10), default="hi") # hi, en, ta, te, bn, gu
    profile_image_url = Column(Text, nullable=True)
    cover_image_url = Column(Text, nullable=True)
    bio = Column(Text, nullable=True)
    location_city = Column(String(100), nullable=True)
    location_state = Column(String(100), nullable=True)
    craft_type = Column(String(100), nullable=True) # e.g. "Handloom Weaver"
    sub_craft = Column(String(100), nullable=True) # e.g. "Textiles"
    rating = Column(Float, default=4.9)
    total_products = Column(Integer, default=24)
    total_sales = Column(Integer, default=150)
    bank_account_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    products = relationship("Product", back_populates="artisan", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="artisan")
    payouts = relationship("Payout", back_populates="artisan")

    @property
    def name(self) -> str:
        return self.full_name or "Ram Kumar"

    @property
    def phone(self) -> str:
        return self.phone_number or "+91 98765 43210"

    @property
    def location(self) -> str:
        if self.location_city and self.location_state:
            return f"{self.location_city}, {self.location_state}"
        return self.location_city or self.location_state or "Varanasi, UP"

    @property
    def craftCategory(self) -> str:
        return self.craft_type or "Handloom Weaver"

    @property
    def subCraft(self) -> str:
        return self.sub_craft or "Textiles"

    @property
    def totalProducts(self) -> int:
        return self.total_products if self.total_products is not None else 24

    @property
    def totalSales(self) -> int:
        return self.total_sales if self.total_sales is not None else 150

    @property
    def avatarUrl(self) -> str:
        return self.profile_image_url or "https://example.com/avatar.jpg"

    @property
    def coverUrl(self) -> str:
        return self.cover_image_url or "https://example.com/cover.jpg"

class Product(Base):
    __tablename__ = "products"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    artisan_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    sku = Column(String(50), index=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    tags = Column(JSON, default=list) # Array of tags e.g. ["Woodcraft", "Handmade", "Storage"]
    price = Column(Float, nullable=False)
    ai_suggested_price = Column(Float, nullable=True)
    confidence_score = Column(Float, default=0.92) # e.g. 0.92 for 92% match
    stock_quantity = Column(Integer, default=3)
    status = Column(String(20), default="PUBLISHED") # DRAFT, PUBLISHED, OUT_OF_STOCK
    image_urls = Column(JSON, default=list)
    raw_audio_url = Column(Text, nullable=True)
    sold_count = Column(Integer, default=14)
    market_benchmark = Column(String(255), default="Similar items sell for ₹550 - ₹700")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    artisan = relationship("User", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")

    @property
    def name(self) -> str:
        return self.title or "Wooden Carved Box"

    @property
    def stock(self) -> int:
        return self.stock_quantity if self.stock_quantity is not None else 0

    @property
    def imageUrl(self) -> str:
        if self.image_urls and isinstance(self.image_urls, list) and len(self.image_urls) > 0:
            return self.image_urls[0]
        return "https://example.com/product1.jpg"

    @property
    def soldCount(self) -> int:
        return self.sold_count if self.sold_count is not None else 14

    @property
    def matchPercentage(self) -> int:
        if self.confidence_score is None:
            return 92
        if self.confidence_score <= 1.0:
            return int(self.confidence_score * 100)
        return int(self.confidence_score)

    @property
    def marketBenchmark(self) -> str:
        return self.market_benchmark or "Similar items sell for ₹550 - ₹700"

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    order_number = Column(String(20), index=True, nullable=False) # e.g. #1029
    buyer_name = Column(String(100), nullable=False)
    buyer_phone = Column(String(20), nullable=True)
    shipping_city = Column(String(100), nullable=False)
    shipping_state = Column(String(100), nullable=False)
    shipping_address_full = Column(Text, nullable=True)
    artisan_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(String(30), default="Pending") # Pending, Processing, Shipped, Delivered, Confirmed, Action_Required
    payment_status = Column(String(20), default="PAID") # PENDING, PAID, REFUNDED
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    artisan = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    @property
    def orderNumber(self) -> str:
        return self.order_number or "#1029"

    @property
    def buyerName(self) -> str:
        return self.buyer_name or "Customer"

    @property
    def buyerPhone(self) -> str:
        return self.buyer_phone or "+91 98123 45678"

    @property
    def shippingCity(self) -> str:
        return self.shipping_city or "Varanasi"

    @property
    def shippingState(self) -> str:
        return self.shipping_state or "Uttar Pradesh"

    @property
    def totalAmount(self) -> float:
        return self.total_amount if self.total_amount is not None else 0.0

    @property
    def paymentStatus(self) -> str:
        return self.payment_status or "PAID"

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    order_id = Column(String(36), ForeignKey("orders.id"), nullable=False)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, nullable=False)
    
    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")

    @property
    def productId(self) -> str:
        return self.product_id

    @property
    def productTitle(self) -> str:
        if hasattr(self, '_product_title') and self._product_title:
            return self._product_title
        if self.product and self.product.title:
            return self.product.title
        return "Wooden Carved Box"

    @property
    def unitPrice(self) -> float:
        return self.unit_price

class Payout(Base):
    __tablename__ = "payouts"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    artisan_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String(20), default="COMPLETED") # PENDING, COMPLETED, FAILED
    gateway_reference = Column(String(100), nullable=True)
    payout_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    artisan = relationship("User", back_populates="payouts")

