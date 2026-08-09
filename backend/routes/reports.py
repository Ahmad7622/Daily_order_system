from fastapi import APIRouter, HTTPException, Query, Response
from backend.database import get_daily_stats, get_weekly_stats
from backend.services.pdf_generator import generate_daily_pdf, generate_weekly_pdf

router = APIRouter()

@router.get("/reports/daily")
def download_daily_report(date: str = Query(..., description="Date (YYYY-MM-DD)")):
    try:
        stats = get_daily_stats(date)
        pdf_bytes = generate_daily_pdf(date, stats)
        
        filename = f"Daily_Order_Report_{date}.pdf"
        headers = {
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": "application/pdf"
        }
        return Response(content=pdf_bytes, headers=headers, media_type="application/pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate daily PDF report: {str(e)}")


@router.get("/reports/weekly")
def download_weekly_report(
    start_date: str = Query(..., description="Start Date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End Date (YYYY-MM-DD)")
):
    try:
        stats = get_weekly_stats(start_date, end_date)
        pdf_bytes = generate_weekly_pdf(start_date, end_date, stats)
        
        filename = f"Weekly_Order_Report_{start_date}_to_{end_date}.pdf"
        headers = {
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": "application/pdf"
        }
        return Response(content=pdf_bytes, headers=headers, media_type="application/pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate weekly PDF report: {str(e)}")
