import os
import sys
import datetime
import streamlit as st

# Add parent project path to sys.path to access backend models and database modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.database import get_daily_stats, get_weekly_stats, get_all_orders, use_supabase
from backend.services.pdf_generator import generate_daily_pdf, generate_weekly_pdf

# Streamlit Page Config
st.set_page_config(
    page_title="Order System - Admin & Reporting",
    page_icon="📦",
    layout="wide"
)

st.title("📦 Daily Order Reporting System — Streamlit Admin Panel")
st.caption("Simplified Admin & PDF Reporting Panel connected to Database")

db_type = "Supabase PostgreSQL" if use_supabase else "SQLite Local Fallback Database"
st.info(f"Connected to Database Mode: **{db_type}**")

st.divider()

# Sidebar controls
st.sidebar.header("⚙️ Reporting Options")
report_type = st.sidebar.radio("Select View / Report Mode", ["Daily Summary & PDF", "Weekly Summary & PDF", "Database View"])

today = datetime.date.today()

if report_type == "Daily Summary & PDF":
    st.subheader("📅 Daily Order Summary & PDF Generation")
    
    selected_date = st.date_input("Select Report Date", value=today)
    date_str = selected_date.strftime("%Y-%m-%d")
    
    stats = get_daily_stats(date_str)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Orders", stats["total_orders"])
    col2.metric("Verified", stats["verified"])
    col3.metric("Pending", stats["pending"])
    col4.metric("Rejected", stats["rejected"])
    col5.metric("Total Sales (PKR)", f"Rs. {stats['total_sales']:,.2f}")
    
    st.divider()
    
    pdf_bytes = generate_daily_pdf(date_str, stats)
    st.download_button(
        label=f"📄 Download Daily Report PDF ({date_str})",
        data=pdf_bytes,
        file_name=f"Daily_Order_Report_{date_str}.pdf",
        mime="application/pdf",
        type="primary"
    )
    
    st.write("### Orders Detail for Selected Date")
    if stats["orders"]:
        st.dataframe(stats["orders"], use_container_width=True)
    else:
        st.warning("No orders found for the selected date.")

elif report_type == "Weekly Summary & PDF":
    st.subheader("📆 Weekly Summary & PDF Report Generation")
    
    col_start, col_end = st.columns(2)
    start_d = col_start.date_input("Start Date", value=today - datetime.timedelta(days=6))
    end_d = col_end.date_input("End Date", value=today)
    
    start_str = start_d.strftime("%Y-%m-%d")
    end_str = end_d.strftime("%Y-%m-%d")
    
    stats = get_weekly_stats(start_str, end_str)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Orders", stats["total_orders"])
    col2.metric("Verified", stats["verified"])
    col3.metric("Pending", stats["pending"])
    col4.metric("Rejected", stats["rejected"])
    col5.metric("Total Sales (PKR)", f"Rs. {stats['total_sales']:,.2f}")
    
    st.divider()
    
    pdf_bytes = generate_weekly_pdf(start_str, end_str, stats)
    st.download_button(
        label=f"📄 Download Weekly Report PDF ({start_str} to {end_str})",
        data=pdf_bytes,
        file_name=f"Weekly_Order_Report_{start_str}_to_{end_str}.pdf",
        mime="application/pdf",
        type="primary"
    )
    
    st.write("### Daily Performance Breakdown")
    if stats["daily_breakdown"]:
        st.table(stats["daily_breakdown"])
    else:
        st.info("No sales breakdown recorded for this range.")
        
    st.write("### All Orders in Date Range")
    if stats["orders"]:
        st.dataframe(stats["orders"], use_container_width=True)

else:
    st.subheader("🗄️ Full Database View")
    orders = get_all_orders()
    st.write(f"Total database records: **{len(orders)}**")
    st.dataframe(orders, use_container_width=True)
