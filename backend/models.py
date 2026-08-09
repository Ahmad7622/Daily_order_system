from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import date

PRODUCT_PRICES = {
    "Plain Shine": 2050.0,
    "Needle Texture": 2050.0,
    "Crocodile Texture": 2050.0,
    "Snake Texture": 2050.0,
    "Softy Grain Leather": 2099.0,
}

VALID_STATUSES = ["Pending", "Verified", "Rejected"]

class OrderBase(BaseModel):
    customer_name: str = Field(..., min_length=1, description="Customer Name")
    phone: str = Field(..., min_length=1, description="Phone Number")
    tracking_id: str = Field(..., min_length=1, description="Tracking ID")
    product_code: str = Field(..., min_length=1, description="Product Code (e.g., PS-01)")
    product_name: str = Field(..., description="Product Name from dropdown")
    amount: Optional[float] = Field(None, description="Order Amount in PKR")
    order_date: str = Field(..., description="Order Date (YYYY-MM-DD)")
    status: str = Field("Pending", description="Status: Pending, Verified, Rejected")

    @validator("product_name")
    def validate_product(cls, v):
        if v not in PRODUCT_PRICES:
            raise ValueError(f"Invalid product name '{v}'. Must be one of: {list(PRODUCT_PRICES.keys())}")
        return v

    @validator("status")
    def validate_status(cls, v):
        if v not in VALID_STATUSES:
            raise ValueError(f"Invalid status '{v}'. Must be one of: {VALID_STATUSES}")
        return v

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    customer_name: Optional[str] = None
    phone: Optional[str] = None
    tracking_id: Optional[str] = None
    product_code: Optional[str] = None
    product_name: Optional[str] = None
    amount: Optional[float] = None
    order_date: Optional[str] = None
    status: Optional[str] = None

class OrderResponse(OrderBase):
    id: int
    amount: float
    created_at: Optional[str] = None

    class Config:
        from_attributes = True
