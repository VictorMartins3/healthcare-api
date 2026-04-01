from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.exc import IntegrityError
import logging
from app.core.database import get_db
from app.models.patient import Patient as PatientModel
from app.schemas.patient import Patient, PatientCreate, PatientResponse

router = APIRouter()
logger = logging.getLogger(__name__)

SORT_FIELDS = {
    "id": PatientModel.id,
    "name": PatientModel.name,
    "date_of_birth": PatientModel.date_of_birth,
    "mrn": PatientModel.mrn,
    "created_at": PatientModel.created_at
}

@router.get("", response_model=PatientResponse)
async def list_patients(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    sort_by: str = Query("id", pattern="^(id|name|date_of_birth|mrn|created_at)$"),
    sort_dir: str = Query("asc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db)
):
    try:
        query = select(PatientModel)
        
        if search:
            search_filter = or_(
                PatientModel.name.ilike(f"%{search}%"),
                PatientModel.mrn.ilike(f"%{search}%")
            )
            query = query.where(search_filter)
        
        total = await db.scalar(select(func.count()).select_from(query.subquery()))
        
        sort_column = SORT_FIELDS[sort_by]
        if sort_dir == "desc":
            sort_column = sort_column.desc()
        query = query.order_by(sort_column)
        
        query = query.offset((page - 1) * per_page).limit(per_page)
        result = await db.execute(query)
        patients = result.scalars().all()
        
        return PatientResponse(
            patients=[Patient.model_validate(p) for p in patients],
            total=total,
            page=page,
            per_page=per_page
        )
    except Exception as e:
        logger.error(f"Error listing patients: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("", status_code=201, response_model=Patient)
async def create_patient(patient: PatientCreate, db: AsyncSession = Depends(get_db)):
    try:
        db_patient = PatientModel(
            name=patient.name,
            date_of_birth=patient.date_of_birth,
            mrn=patient.mrn
        )
        db.add(db_patient)
        await db.commit()
        await db.refresh(db_patient)
        return Patient.model_validate(db_patient)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Patient with this MRN already exists")
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating patient: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{patient_id}", response_model=Patient)
async def get_patient(patient_id: int, db: AsyncSession = Depends(get_db)):
    try:
        patient = await db.get(PatientModel, patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        return Patient.model_validate(patient)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching patient {patient_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{patient_id}", response_model=Patient)
async def update_patient(patient_id: int, patient: PatientCreate, db: AsyncSession = Depends(get_db)):
    try:
        db_patient = await db.get(PatientModel, patient_id)
        if not db_patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        db_patient.name = patient.name
        db_patient.date_of_birth = patient.date_of_birth
        db_patient.mrn = patient.mrn
        
        await db.commit()
        await db.refresh(db_patient)
        return Patient.model_validate(db_patient)
    except HTTPException:
        raise
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="MRN already exists")
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating patient {patient_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{patient_id}", status_code=204)
async def delete_patient(patient_id: int, db: AsyncSession = Depends(get_db)):
    try:
        patient = await db.get(PatientModel, patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        await db.delete(patient)
        await db.commit()
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting patient {patient_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
