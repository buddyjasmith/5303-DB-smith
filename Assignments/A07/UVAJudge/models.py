import datetime
from typing import Optional
from pydantic import BaseModel, Field

class NewClassModel(BaseModel):
    document_id: str
    class_name: str
class UpdateClassModel(BaseModel):
    class_name: str
class PdfModel(BaseModel):
    uva_probem_id: int
