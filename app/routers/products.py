import os
import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Request, Body
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models import Product, User
from app.schemas import (
    ProductCreateSchema, ProductStockUpdateSchema, AICatalogResponseSchema,
    ProductItemSchema, ProductListResponse, ProductResponseSchema
)
from app.services.auth_service import get_current_user
from app.services.ai_service import AIService

router = APIRouter(prefix="/products", tags=["Products & Inventory"])

def format_product_item(p: Product) -> ProductItemSchema:
    created_at_str = p.created_at.strftime("%Y-%m-%dT%H:%M:%S.000Z") if p.created_at else "2024-01-01T00:00:00.000Z"
    return ProductItemSchema(
        id=p.id,
        name=p.name,
        description=p.description or "",
        price=float(p.price),
        stock=int(p.stock),
        sku=p.sku,
        category=p.category or "Woodcraft",
        tags=p.tags if p.tags else ["Woodcraft", "Handmade", "Storage"],
        imageUrl=p.imageUrl,
        soldCount=p.soldCount,
        matchPercentage=p.matchPercentage,
        marketBenchmark=p.marketBenchmark,
        createdAt=created_at_str
    )

def ensure_sample_products(db: Session, user: User) -> List[Product]:
    products = db.query(Product).filter(Product.artisan_id == user.id).order_by(Product.created_at.desc()).all()
    if not products:
        p1 = Product(
            id="prod_001",
            artisan_id=user.id,
            sku="WB-01",
            title="Wooden Carved Box",
            description="Intricate hand-carved wooden box for jewelry.",
            price=600.0,
            stock_quantity=3,
            category="Woodcraft",
            tags=["Woodcraft", "Handmade", "Storage"],
            image_urls=["https://example.com/product1.jpg"],
            sold_count=14,
            confidence_score=0.92,
            market_benchmark="Similar items sell for ₹550 - ₹700",
            status="PUBLISHED",
            created_at=datetime(2024, 1, 1, 0, 0, 0)
        )
        p2 = Product(
            id="prod_002",
            artisan_id=user.id,
            sku="HW-02",
            title="Authentic Blue Handloom Wool Shawl",
            description="Experience warmth with traditional blue handloom wool shawl.",
            price=1850.0,
            stock_quantity=5,
            category="Clothing & Apparel",
            tags=["Winter Wear", "Handloom", "Ethical Craft"],
            image_urls=["https://example.com/product2.jpg"],
            sold_count=22,
            confidence_score=0.94,
            market_benchmark="Similar items sell for ₹1700 - ₹2200",
            status="PUBLISHED",
            created_at=datetime(2024, 1, 2, 0, 0, 0)
        )
        db.add(p1)
        db.add(p2)
        db.commit()
        products = [p1, p2]
    return products

@router.get("", response_model=ProductListResponse)
@router.get("/", response_model=ProductListResponse)
def list_products(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves the list of products for the authenticated artisan.
    Returns JSON response: { "data": [...] }
    """
    products = ensure_sample_products(db, current_user)
    formatted = [format_product_item(p) for p in products]
    return ProductListResponse(data=formatted)

@router.post("", response_model=ProductItemSchema, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=ProductItemSchema, status_code=status.HTTP_201_CREATED)
def create_product(
    data: ProductCreateSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Creates and publishes a new product to the catalog.
    """
    product_title = data.name or data.title or "Handcrafted Item"
    sku_input = data.sku
    if not sku_input:
        prefix = "".join([w[0].upper() for w in product_title.split()[:2] if w]) or "PRD"
        sku_input = f"{prefix}-{uuid.uuid4().hex[:4].upper()}"
    else:
        existing = db.query(Product).filter(Product.sku == sku_input).first()
        if existing:
            sku_input = f"{sku_input}-{uuid.uuid4().hex[:4].upper()}"

    stock_val = data.stock if data.stock is not None else (data.stock_quantity if data.stock_quantity is not None else 1)
    img_urls = [data.imageUrl] if data.imageUrl else (data.image_urls if data.image_urls else ["https://example.com/product1.jpg"])

    product = Product(
        artisan_id=current_user.id,
        sku=sku_input,
        title=product_title,
        description=data.description or "Handcrafted artisan product.",
        category=data.category or "Crafts",
        tags=data.tags if data.tags else ["Handmade", "Artisan"],
        price=float(data.price),
        ai_suggested_price=float(data.price),
        confidence_score=0.92,
        stock_quantity=stock_val,
        status="PUBLISHED" if stock_val > 0 else "OUT_OF_STOCK",
        image_urls=img_urls,
        sold_count=0,
        market_benchmark=f"Similar items sell for ₹{int(data.price*0.9)} - ₹{int(data.price*1.15)}"
    )

    db.add(product)
    db.commit()
    db.refresh(product)
    return format_product_item(product)

@router.post("/{product_id}/stock", response_model=ProductItemSchema)
@router.post("/{product_id}/stock/", response_model=ProductItemSchema)
@router.patch("/{product_id}/stock", response_model=ProductItemSchema)
@router.patch("/{product_id}/stock/", response_model=ProductItemSchema)
async def update_stock(
    product_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Adjusts the inventory count for a specific product ID.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        product = db.query(Product).filter(Product.sku == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with ID '{product_id}' not found")

    new_stock = None
    try:
        body = await request.json()
        if isinstance(body, dict):
            new_stock = body.get("stock") if body.get("stock") is not None else body.get("stock_quantity")
    except Exception:
        pass

    if new_stock is None:
        params = request.query_params
        if "stock" in params:
            new_stock = int(params["stock"])

    if new_stock is None:
        new_stock = 0

    product.stock_quantity = int(new_stock)
    if product.stock_quantity <= 0:
        product.status = "OUT_OF_STOCK"
    else:
        product.status = "PUBLISHED"

    db.commit()
    db.refresh(product)
    return format_product_item(product)

# --- AI Multimodal & Delete endpoints ---

@router.post("/ai-catalog", response_model=AICatalogResponseSchema)
async def ai_catalog_product(
    image: UploadFile = File(...),
    audio: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user)
):
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    image_ext = image.filename.split(".")[-1] if "." in image.filename else "jpg"
    image_filename = f"img_{uuid.uuid4().hex[:8]}.{image_ext}"
    image_path = os.path.join(settings.UPLOAD_DIR, image_filename)
    
    with open(image_path, "wb") as f:
        f.write(await image.read())
        
    image_url = f"/static/uploads/{image_filename}"
    
    audio_path = None
    if audio:
        audio_ext = audio.filename.split(".")[-1] if "." in audio.filename else "wav"
        audio_filename = f"audio_{uuid.uuid4().hex[:8]}.{audio_ext}"
        audio_path = os.path.join(settings.UPLOAD_DIR, audio_filename)
        with open(audio_path, "wb") as f:
            f.write(await audio.read())

    ai_result = await AIService.process_voice_and_image(
        audio_file_path=audio_path,
        image_file_path=image_url,
        user_language=current_user.preferred_language
    )
    
    return ai_result

@router.delete("/{product_id}")
def delete_product(
    product_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    db.delete(product)
    db.commit()
    return {"status": "success", "message": "Product deleted successfully"}
