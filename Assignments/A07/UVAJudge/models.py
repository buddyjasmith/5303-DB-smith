import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

class ClassModel(BaseModel):
    document_id: str = None
    semester: str = None

class UpdateClassModel(BaseModel):
    class_name: str

class PdfModel(BaseModel):
    uva_probem_id: int

class Assignment(BaseModel):
    semester: str = None
    assn_number: str = None
    title: List[str] = None
    required: int = None
    uva_id: List[int] = None
    percent: List[float] = None
    
    due_date: str = None
    time_due: str = None
    unix_datetime: str = None
    weight: List[float] = None
    