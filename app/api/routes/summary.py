from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging
from app.core.database import get_db
from app.models.patient import Patient as PatientModel, Note as NoteModel
from app.schemas.patient import Summary
from app.services.summary_service import SummaryService

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/patients/{patient_id}/summary", response_model=Summary)
async def get_patient_summary(
    patient_id: int,
    audience: str = Query("clinician", pattern="^(clinician|family)$"),
    db: AsyncSession = Depends(get_db)
):
    try:
        patient = await db.get(PatientModel, patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Fetch notes for this patient
        result = await db.execute(
            select(NoteModel).where(NoteModel.patient_id == patient_id).order_by(NoteModel.taken_at)
        )
        notes = result.scalars().all()
        
        summary, key_findings = await SummaryService.generate_summary(patient, notes, audience)
        
        return Summary(
            patient_id=patient_id,
            summary=summary,
            key_findings=key_findings,
            audience=audience
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
