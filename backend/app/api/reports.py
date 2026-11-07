from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any

from app.api.auth import get_current_user
from app.models.schemas import UserInDB
from app.utils.pdf_generator import create_report_pdf

router = APIRouter()

class ReportRequest(BaseModel):
    report_type: str # 'disease', 'soil', 'yield'
    data: Dict[str, Any]

@router.post("/reports/generate")
async def generate_report(
    req: ReportRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Generate and download a PDF report.
    """
    if req.report_type not in ["disease", "soil", "yield"]:
        raise HTTPException(status_code=400, detail="Invalid report type")

    titles = {
        "disease": "Crop Disease Diagnosis Report",
        "soil": "Soil Health Analysis Report",
        "yield": "AI Yield Forecast Report"
    }

    try:
        pdf_buffer = create_report_pdf(
            title=titles[req.report_type],
            user_name=current_user.name,
            data=req.data,
            report_type=req.report_type
        )
        
        headers = {
            'Content-Disposition': f'attachment; filename="kisaan_mitra_{req.report_type}_report.pdf"'
        }
        
        return StreamingResponse(pdf_buffer, headers=headers, media_type="application/pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")
