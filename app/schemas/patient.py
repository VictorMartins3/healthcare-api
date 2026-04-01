from datetime import datetime, date
from typing import List
from pydantic import BaseModel, Field

class PatientCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    date_of_birth: date
    mrn: str = Field(..., min_length=1, max_length=50)

class Patient(BaseModel):
    id: int
    name: str
    date_of_birth: date
    mrn: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PatientResponse(BaseModel):
    patients: List[Patient]
    total: int
    page: int
    per_page: int

class NoteCreate(BaseModel):
    content: str = Field(..., min_length=1)
    taken_at: datetime

class Note(BaseModel):
    id: int
    patient_id: int
    content: str
    taken_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True

class NotesResponse(BaseModel):
    notes: List[Note]
    total: int
    page: int
    per_page: int

class Summary(BaseModel):
    patient_id: int
    summary: str
    key_findings: List[str]
    audience: str
