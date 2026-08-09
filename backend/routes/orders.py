from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
from datetime import date

from backend.models import OrderCreate, OrderUpdate, OrderResponse, PRODUCT_PRICES
from backend.database import (
    get_all_orders,
    get_order_by_id,
    create_order,
    update_order,
    delete_order,
    get_daily_stats,
    get_weekly_stats
)

router = APIRouter()

@router.get("/orders", response_model=List[OrderResponse])
def read_orders(
    search: Optional[str] = Query(None, description="Search by customer, phone, tracking ID, product code, or ID"),
    status: Optional[str] = Query(None, description="Filter by status (All, Pending, Verified, Rejected)"),
    order_date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    start_date: Optional[str] = Query(None, description="Start date for range filter"),
    end_date: Optional[str] = Query(None, description="End date for range filter")
):
    try:
        orders = get_all_orders(
            search=search,
            status=status,
            order_date=order_date,
            start_date=start_date,
            end_date=end_date
        )
        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch orders: {str(e)}")


@router.get("/orders/{order_id}", response_model=OrderResponse)
def read_order(order_id: int):
    order = get_order_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Order #{order_id} not found")
    return order


@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def add_order(order_in: OrderCreate):
    try:
        # Enforce server-side product price validation (Requirement 21)
        expected_price = PRODUCT_PRICES.get(order_in.product_name)
        if expected_price is None:
            raise HTTPException(status_code=400, detail=f"Invalid product selection: {order_in.product_name}")
            
        data = order_in.dict()
        data["amount"] = expected_price  # Always use authoritative server price
        
        new_order = create_order(data)
        return new_order
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save order: {str(e)}")


@router.put("/orders/{order_id}", response_model=OrderResponse)
def edit_order(order_id: int, order_in: OrderUpdate):
    existing = get_order_by_id(order_id)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Order #{order_id} not found")
        
    data = order_in.dict(exclude_unset=True)
    
    # If product_name is modified, update amount automatically according to server price table
    if "product_name" in data and data["product_name"]:
        p_name = data["product_name"]
        if p_name not in PRODUCT_PRICES:
            raise HTTPException(status_code=400, detail=f"Invalid product selection: {p_name}")
        data["amount"] = PRODUCT_PRICES[p_name]
        
    try:
        updated = update_order(order_id, data)
        if not updated:
            raise HTTPException(status_code=500, detail="Failed to update order")
        return updated
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update order: {str(e)}")


@router.delete("/orders/{order_id}")
def remove_order(order_id: int):
    existing = get_order_by_id(order_id)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Order #{order_id} not found")
        
    success = delete_order(order_id)
    if not success:
        raise HTTPException(status_code=500, detail=f"Failed to delete order #{order_id}")
        
    return {"message": f"Order #{order_id} deleted successfully"}


@router.get("/stats/daily")
def daily_stats(date: str = Query(..., description="Date (YYYY-MM-DD)")):
    try:
        return get_daily_stats(date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load daily stats: {str(e)}")


@router.get("/stats/weekly")
def weekly_stats(
    start_date: str = Query(..., description="Start Date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End Date (YYYY-MM-DD)")
):
    try:
        return get_weekly_stats(start_date, end_date)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load weekly stats: {str(e)}")
