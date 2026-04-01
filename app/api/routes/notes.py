from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import logging
from app.core.database import get_db
from app.models.patient import Patient as PatientModel, Note as NoteModel
from app.schemas.patient import Note, NoteCreate, NotesResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/patients/{patient_id}/notes", status_code=201, response_model=Note)
async def create_note(patient_id: int, note: NoteCreate, db: AsyncSession = Depends(get_db)):
    try:
        patient = await db.get(PatientModel, patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        db_note = NoteModel(
            patient_id=patient_id,
            content=note.content,
            taken_at=note.taken_at
        )
        db.add(db_note)
        await db.commit()
        await db.refresh(db_note)
        return Note.model_validate(db_note)
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating note: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/patients/{patient_id}/notes", response_model=NotesResponse)
async def get_notes(
    patient_id: int,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    try:
        patient = await db.get(PatientModel, patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        query = select(NoteModel).where(NoteModel.patient_id == patient_id)
        total = await db.scalar(select(func.count()).select_from(query.subquery()))
        
        query = query.order_by(NoteModel.taken_at.desc())
        query = query.offset((page - 1) * per_page).limit(per_page)
        result = await db.execute(query)
        notes = result.scalars().all()
        
        return NotesResponse(
            notes=[Note.model_validate(n) for n in notes],
            total=total,
            page=page,
            per_page=per_page
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching notes: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/patients/{patient_id}/notes/{note_id}", status_code=204)
async def delete_note(patient_id: int, note_id: int, db: AsyncSession = Depends(get_db)):
    try:
        query = select(NoteModel).where(NoteModel.id == note_id, NoteModel.patient_id == patient_id)
        result = await db.execute(query)
        note = result.scalar_one_or_none()
        
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        await db.delete(note)
        await db.commit()
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting note: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
