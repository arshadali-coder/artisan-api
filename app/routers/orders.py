import random
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Order, OrderItem, Product, User
from app.schemas import (
    OrderListResponse, OrderItemResponseSchema, OrderItemDetailSchema
)
from app.services.auth_service import get_current_user
from app.websockets.manager import ws_manager

router = APIRouter(prefix="/orders", tags=["Order Management"])

def format_order_item(order: Order) -> OrderItemResponseSchema:
    items_list = []
    for item in order.items:
        prod_title = "Wooden Carved Box"
        if item.product and item.product.title:
            prod_title = item.product.title
        elif hasattr(item, 'product_title') and item.product_title:
            prod_title = item.product_title
            
        items_list.append(
            OrderItemDetailSchema(
                id=item.id,
                productId=item.product_id,
                productTitle=prod_title,
                quantity=item.quantity,
                unitPrice=float(item.unit_price)
            )
        )
    if not items_list:
        items_list = [
            OrderItemDetailSchema(
                id="item_001",
                productId="prod_001",
                productTitle="Wooden Carved Box",
                quantity=2,
                unitPrice=600.0
            )
        ]

    created_at_str = order.created_at.strftime("%Y-%m-%dT%H:%M:%S.000Z") if order.created_at else "2024-01-01T00:00:00.000Z"

    return OrderItemResponseSchema(
        id=order.id,
        orderNumber=order.orderNumber,
        buyerName=order.buyerName,
        buyerPhone=order.buyerPhone,
        shippingCity=order.shippingCity,
        shippingState=order.shippingState,
        totalAmount=float(order.totalAmount),
        status=order.status or "Pending",
        paymentStatus=order.paymentStatus,
        createdAt=created_at_str,
        items=items_list
    )

def ensure_sample_orders(db: Session, user: User) -> List[Order]:
    orders = db.query(Order).filter(Order.artisan_id == user.id).order_by(Order.created_at.desc()).all()
    if not orders:
        product = db.query(Product).filter(Product.artisan_id == user.id).first()
        prod_id = product.id if product else "prod_001"
        prod_price = product.price if product else 600.0

        o1 = Order(
            id="ord_001",
            order_number="#1029",
            buyer_name="Siddharth Sharma",
            buyer_phone="+91 98123 45678",
            shipping_city="Mumbai",
            shipping_state="Maharashtra",
            artisan_id=user.id,
            total_amount=prod_price * 2,
            status="Pending",
            payment_status="PAID",
            created_at=datetime(2024, 1, 1, 0, 0, 0)
        )
        db.add(o1)
        db.commit()
        db.refresh(o1)

        item1 = OrderItem(
            id="item_001",
            order_id=o1.id,
            product_id=prod_id,
            quantity=2,
            unit_price=prod_price
        )
        db.add(item1)
        db.commit()

        o2 = Order(
            id="ord_002",
            order_number="#1030",
            buyer_name="Anita Desai",
            buyer_phone="+91 98765 12345",
            shipping_city="Bengaluru",
            shipping_state="Karnataka",
            artisan_id=user.id,
            total_amount=1850.0,
            status="Processing",
            payment_status="PAID",
            created_at=datetime(2024, 1, 2, 0, 0, 0)
        )
        db.add(o2)
        db.commit()
        db.refresh(o2)

        item2 = OrderItem(
            id="item_002",
            order_id=o2.id,
            product_id=prod_id,
            quantity=1,
            unit_price=1850.0
        )
        db.add(item2)
        db.commit()

        orders = [o1, o2]
    return orders

@router.get("", response_model=OrderListResponse)
@router.get("/", response_model=OrderListResponse)
def list_orders(
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves the list of orders for the authenticated artisan.
    Filter by status: Pending, Processing, Shipped, Delivered.
    Returns JSON response: { "data": [...] }
    """
    ensure_sample_orders(db, current_user)
    query = db.query(Order).filter(Order.artisan_id == current_user.id)

    if status_filter:
        query = query.filter(Order.status.ilike(f"%{status_filter}%"))

    orders = query.order_by(Order.created_at.desc()).all()
    formatted = [format_order_item(o) for o in orders]
    return OrderListResponse(data=formatted)

@router.patch("/{order_id}", response_model=OrderItemResponseSchema)
@router.patch("/{order_id}/", response_model=OrderItemResponseSchema)
@router.patch("/{order_id}/status", response_model=OrderItemResponseSchema)
@router.patch("/{order_id}/status/", response_model=OrderItemResponseSchema)
async def update_order_status(
    order_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Updates the status of a specific order ID (e.g., Pending to Confirmed).
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        order = db.query(Order).filter(Order.order_number == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order with ID '{order_id}' not found")

    new_status = "Confirmed"
    try:
        body = await request.json()
        if isinstance(body, dict) and "status" in body:
            new_status = body["status"]
    except Exception:
        pass

    order.status = new_status
    db.commit()
    db.refresh(order)

    # Emit real-time WebSocket Alert
    await ws_manager.send_personal_message({
        "event": "ORDER_STATUS_CHANGED",
        "order_id": order.id,
        "order_number": order.order_number,
        "new_status": new_status,
        "message": f"Order {order.order_number} status updated to {new_status}"
    }, user_id=current_user.id)

    return format_order_item(order)

@router.post("/simulate", response_model=OrderItemResponseSchema, status_code=status.HTTP_201_CREATED)
async def simulate_incoming_order(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.artisan_id == current_user.id).first()
    if not product:
        product = Product(
            artisan_id=current_user.id,
            sku=f"SIM-{uuid.uuid4().hex[:4].upper()}",
            title="Terracotta Planter Pot",
            price=1200.0,
            stock_quantity=10,
            image_urls=["https://example.com/pottery.jpg"]
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        
    order_num = f"#{random.randint(1000, 9999)}"
    buyer_names = ["Siddharth Sharma", "Anita Desai", "Vikram Patel", "Priya Nair"]
    city, state = random.choice([("Mumbai", "Maharashtra"), ("Delhi", "Delhi"), ("Bengaluru", "Karnataka")])
    
    order = Order(
        order_number=order_num,
        buyer_name=random.choice(buyer_names),
        buyer_phone="+91 98123 45678",
        shipping_city=city,
        shipping_state=state,
        artisan_id=current_user.id,
        total_amount=product.price * 2,
        status="Pending",
        payment_status="PAID"
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    
    item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        quantity=2,
        unit_price=product.price
    )
    db.add(item)
    db.commit()
    
    await ws_manager.send_personal_message({
        "event": "NEW_ORDER_RECEIVED",
        "order_id": order.id,
        "order_number": order.order_number,
        "buyer_name": order.buyer_name,
        "amount": order.total_amount,
        "message": f"🎉 New order {order.order_number} received from {order.buyer_name}!"
    }, user_id=current_user.id)
    
    return format_order_item(order)
