# C:\Users\Faith\Downloads\myits-collab\backend\app\schemas\application.py

from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Optional, List

# Document Schemas
class DokumenBase(BaseModel):
    nama_dokumen: str = Field(..., max_length=100, alias="Nama_Dokumen")
    file_path: str = Field(..., alias="File_Path") # This will be the URL or path to the file

class DokumenCreate(DokumenBase):
    # No ID_Dokumen as it's auto-incremented
    pass

class DokumenResponse(DokumenBase):
    id_dokumen: int = Field(..., alias="ID_Dokumen")
    tgl_upload: datetime = Field(..., alias="Tgl_Upload")

    class Config:
        from_attributes = True
        populate_by_name = True

# Application (Transaksi_Mahasiswa_Proyek) Schemas
class ApplicationBase(BaseModel):
    # No ID_Pendaftaran, Mahasiswa_NRP, Proyek_ID_Proyek for base input
    status: bool = Field(False, alias="Status") # Default to False (pending)

class ApplicationCreate(ApplicationBase):
    # For creation, we generally don't send status, it's pending by default
    # The project_id will be in the URL path, student_nrp from token
    pass

class ApplicationResponse(ApplicationBase):
    mahasiswa_nrp: str = Field(..., alias="Mahasiswa_NRP")
    proyek_id: str = Field(..., alias="Proyek_ID_Proyek")
    id_pendaftaran: str = Field(..., alias="ID_Pendaftaran")
    tgl_apply: Optional[datetime] = None # You might want to add this field to your model for consistency

    # Include associated documents
    documents: List[DokumenResponse] = [] # List of linked documents

    class Config:
        from_attributes = True
        populate_by_name = True