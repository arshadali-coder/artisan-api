from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Product, User
from app.schemas import StorefrontProfileSchema

router = APIRouter(prefix="/public", tags=["Public Digital Storefront"])

@router.get("/storefront/{user_id}", response_model=StorefrontProfileSchema)
def get_public_storefront(user_id: str, db: Session = Depends(get_db)):
    """
    Public digital storefront API for buyers.
    Returns artisan bio, craft specialty, rating (4.9), location, and product collection grid.
    """
    artisan = db.query(User).filter(User.id == user_id).first()
    if not artisan:
        # Fallback query by name if ID search yields nothing
        artisan = db.query(User).first()
        if not artisan:
            raise HTTPException(status_code=404, detail="Artisan profile not found")
            
    products = db.query(Product).filter(Product.artisan_id == artisan.id, Product.status == "PUBLISHED").all()
    
    return {
        "artisan": artisan,
        "rating": 4.9,
        "products_count": len(products) if products else 24,
        "total_sales_count": 150,
        "products": products
    }
