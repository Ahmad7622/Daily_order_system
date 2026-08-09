import os
import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip()

supabase_client = None
use_supabase = False

if SUPABASE_URL and SUPABASE_KEY and "your-supabase" not in SUPABASE_URL:
    try:
        from supabase import create_client, Client
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        use_supabase = True
        print("Connected to Supabase PostgreSQL Database!")
    except Exception as e:
        print(f"Failed to connect to Supabase: {e}. Falling back to SQLite local database.")
        use_supabase = False

# SQLite Local Fallback Database
DB_FILE = os.path.join(os.path.dirname(__file__), "..", "orders.db")

def init_sqlite_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            tracking_id TEXT NOT NULL,
            product_code TEXT NOT NULL,
            product_name TEXT NOT NULL,
            amount REAL NOT NULL,
            order_date TEXT NOT NULL,
            status TEXT NOT NULL CHECK (status IN ('Pending', 'Verified', 'Rejected')),
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()

if not use_supabase:
    init_sqlite_db()


def get_all_orders(
    search: Optional[str] = None,
    status: Optional[str] = None,
    order_date: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Dict[str, Any]]:
    if use_supabase and supabase_client:
        query = supabase_client.table("orders").select("*")
        if status and status.lower() != "all":
            query = query.eq("status", status)
        if order_date:
            query = query.eq("order_date", order_date)
        if start_date and end_date:
            query = query.gte("order_date", start_date).lte("order_date", end_date)
        
        response = query.order("id", desc=True).execute()
        orders = response.data or []
        
        if search:
            search_lower = search.lower()
            orders = [
                o for o in orders
                if search_lower in str(o.get("customer_name", "")).lower()
                or search_lower in str(o.get("phone", "")).lower()
                or search_lower in str(o.get("tracking_id", "")).lower()
                or search_lower in str(o.get("product_code", "")).lower()
                or search_lower in str(o.get("id", "")).lower()
            ]
        return orders
    else:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        sql = "SELECT * FROM orders WHERE 1=1"
        params = []
        
        if status and status.lower() != "all":
            sql += " AND status = ?"
            params.append(status)
        if order_date:
            sql += " AND order_date = ?"
            params.append(order_date)
        if start_date and end_date:
            sql += " AND order_date >= ? AND order_date <= ?"
            params.extend([start_date, end_date])
            
        sql += " ORDER BY id DESC"
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        orders = [dict(row) for row in rows]
        conn.close()
        
        if search:
            search_lower = search.lower()
            orders = [
                o for o in orders
                if search_lower in str(o.get("customer_name", "")).lower()
                or search_lower in str(o.get("phone", "")).lower()
                or search_lower in str(o.get("tracking_id", "")).lower()
                or search_lower in str(o.get("product_code", "")).lower()
                or search_lower in str(o.get("id", "")).lower()
            ]
        return orders


def get_order_by_id(order_id: int) -> Optional[Dict[str, Any]]:
    if use_supabase and supabase_client:
        response = supabase_client.table("orders").select("*").eq("id", order_id).execute()
        data = response.data
        return data[0] if data else None
    else:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None


def create_order(order_data: Dict[str, Any]) -> Dict[str, Any]:
    if use_supabase and supabase_client:
        response = supabase_client.table("orders").insert(order_data).execute()
        if response.data:
            return response.data[0]
        raise Exception("Failed to insert order into Supabase")
    else:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO orders (customer_name, phone, tracking_id, product_code, product_name, amount, order_date, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            order_data["customer_name"],
            order_data["phone"],
            order_data["tracking_id"],
            order_data["product_code"],
            order_data["product_name"],
            order_data["amount"],
            order_data["order_date"],
            order_data["status"]
        ))
        conn.commit()
        new_id = cursor.lastrowid
        cursor.execute("SELECT * FROM orders WHERE id = ?", (new_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else order_data


def update_order(order_id: int, order_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    # Remove None values
    clean_data = {k: v for k, v in order_data.items() if v is not None}
    if not clean_data:
        return get_order_by_id(order_id)
        
    if use_supabase and supabase_client:
        response = supabase_client.table("orders").update(clean_data).eq("id", order_id).execute()
        return response.data[0] if response.data else None
    else:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        set_clause = ", ".join([f"{k} = ?" for k in clean_data.keys()])
        values = list(clean_data.values()) + [order_id]
        
        cursor.execute(f"UPDATE orders SET {set_clause} WHERE id = ?", values)
        conn.commit()
        cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None


def delete_order(order_id: int) -> bool:
    if use_supabase and supabase_client:
        response = supabase_client.table("orders").delete().eq("id", order_id).execute()
        return len(response.data) > 0 if response.data else True
    else:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM orders WHERE id = ?", (order_id,))
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0


def get_daily_stats(order_date: str) -> Dict[str, Any]:
    orders = get_all_orders(order_date=order_date)
    total_orders = len(orders)
    verified = sum(1 for o in orders if o.get("status") == "Verified")
    pending = sum(1 for o in orders if o.get("status") == "Pending")
    rejected = sum(1 for o in orders if o.get("status") == "Rejected")
    # Total sales sum for all non-rejected or verified orders
    # Requirements specify total sales calculated from all orders of that date or verified
    total_sales = sum(float(o.get("amount", 0)) for o in orders if o.get("status") in ["Verified", "Pending"])
    
    return {
        "date": order_date,
        "total_orders": total_orders,
        "verified": verified,
        "pending": pending,
        "rejected": rejected,
        "total_sales": total_sales,
        "orders": orders
    }


def get_weekly_stats(start_date: str, end_date: str) -> Dict[str, Any]:
    orders = get_all_orders(start_date=start_date, end_date=end_date)
    total_orders = len(orders)
    verified = sum(1 for o in orders if o.get("status") == "Verified")
    pending = sum(1 for o in orders if o.get("status") == "Pending")
    rejected = sum(1 for o in orders if o.get("status") == "Rejected")
    total_sales = sum(float(o.get("amount", 0)) for o in orders if o.get("status") in ["Verified", "Pending"])
    
    # Daily breakdown
    daily_map = {}
    for o in orders:
        d = o.get("order_date")
        if d not in daily_map:
            daily_map[d] = {"date": d, "orders": 0, "sales": 0.0}
        daily_map[d]["orders"] += 1
        if o.get("status") in ["Verified", "Pending"]:
            daily_map[d]["sales"] += float(o.get("amount", 0))
            
    daily_breakdown = sorted(daily_map.values(), key=lambda x: x["date"])
    
    return {
        "start_date": start_date,
        "end_date": end_date,
        "total_orders": total_orders,
        "verified": verified,
        "pending": pending,
        "rejected": rejected,
        "total_sales": total_sales,
        "daily_breakdown": daily_breakdown,
        "orders": orders
    }
