import os
from datetime import date
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.routes.orders import router as orders_router
from backend.routes.reports import router as reports_router
from backend.database import get_all_orders, create_order
from backend.models import PRODUCT_PRICES

app = FastAPI(
    title="Daily Customer Order Reporting System",
    description="E-commerce daily order recording and daily/weekly PDF reporting system",
    version="1.0.0"
)

# CORS Middleware Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(orders_router, prefix="/api", tags=["Orders & Stats"])
app.include_router(reports_router, prefix="/api", tags=["Reports"])

# Static Files Path
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

@app.on_event("startup")
def seed_sample_data_if_empty():
    """Seed initial sample orders for testing if database is currently empty."""
    try:
        existing = get_all_orders()
        if not existing:
            today_str = date.today().isoformat()
            sample_orders = [
                {
                    "customer_name": "Ahmad Ali",
                    "phone": "03001234567",
                    "tracking_id": "TRX123456789",
                    "product_code": "PS-01",
                    "product_name": "Plain Shine",
                    "amount": PRODUCT_PRICES["Plain Shine"],
                    "order_date": today_str,
                    "status": "Verified"
                },
                {
                    "customer_name": "Usman Khan",
                    "phone": "03219876543",
                    "tracking_id": "TRX987654321",
                    "product_code": "NT-02",
                    "product_name": "Needle Texture",
                    "amount": PRODUCT_PRICES["Needle Texture"],
                    "order_date": today_str,
                    "status": "Pending"
                },
                {
                    "customer_name": "Hamza Tariq",
                    "phone": "03451122334",
                    "tracking_id": "TRX445566778",
                    "product_code": "CT-03",
                    "product_name": "Crocodile Texture",
                    "amount": PRODUCT_PRICES["Crocodile Texture"],
                    "order_date": today_str,
                    "status": "Verified"
                },
                {
                    "customer_name": "Bilal Sheikh",
                    "phone": "03125566778",
                    "tracking_id": "TRX332211004",
                    "product_code": "ST-04",
                    "product_name": "Snake Texture",
                    "amount": PRODUCT_PRICES["Snake Texture"],
                    "order_date": today_str,
                    "status": "Rejected"
                },
                {
                    "customer_name": "Zain Malik",
                    "phone": "03337788990",
                    "tracking_id": "TRX998877665",
                    "product_code": "SG-05",
                    "product_name": "Softy Grain Leather",
                    "amount": PRODUCT_PRICES["Softy Grain Leather"],
                    "order_date": today_str,
                    "status": "Verified"
                }
            ]
            for o in sample_orders:
                create_order(o)
            print("Sample seed data successfully populated!")
    except Exception as e:
        print(f"Startup seeding notice: {e}")

# Mount static frontend files
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
def serve_index():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Daily Order Reporting System API is running. Frontend index.html not found."}
