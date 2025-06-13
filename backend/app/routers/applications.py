# C:\Users\Faith\Downloads\myits-collab\backend\app\routers\applications.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.schemas import applications as application_schema
from app.services import applications_service
# from app.core.security import get_current_active_user # For authentication later
# from app.models import user as user_model # For user types in Depends

router = APIRouter(
    prefix="/applications",
    tags=["Applications"]
)

# Endpoint for uploader to view an application's details or update status
@router.get("/{mahasiswa_nrp}/{proyek_id}/{id_pendaftaran}", response_model=application_schema.ApplicationResponse)
# Requires authentication: current_user = Depends(get_current_active_user)
def get_application_details(
    mahasiswa_nrp: str,
    proyek_id: str,
    id_pendaftaran: str,
    db: Session = Depends(get_db)
):
    db_application = applications_service.get_application_by_id(db, mahasiswa_nrp, proyek_id, id_pendaftaran)
    if not db_application:
        raise HTTPException(status_code=404, detail="Application not found")

    # Authorization check: only the project uploader or admin can view/manage this application
    # project_uploader_id = db_application.proyek.Admin_ID_Admin or db_application.proyek.Dosen_NIP
    # if current_user.id != project_uploader_id and current_user.role != 'admin':
    #     raise HTTPException(status_code=403, detail="Not authorized to view this application")

    return db_application

@router.put("/{mahasiswa_nrp}/{proyek_id}/{id_pendaftaran}/status", response_model=application_schema.ApplicationResponse)
# Requires authentication: current_user = Depends(get_current_active_user)
def update_application_status(
    mahasiswa_nrp: str,
    proyek_id: str,
    id_pendaftaran: str,
    new_status: bool, # True for accept, False for reject
    db: Session = Depends(get_db)
):
    # Authorization check: only the project uploader or admin can update status
    # project_uploader_id = db_application.proyek.Admin_ID_Admin or db_application.proyek.Dosen_NIP
    # if current_user.id != project_uploader_id and current_user.role != 'admin':
    #     raise HTTPException(status_code=403, detail="Not authorized to update this application status")

    updated_application = applications_service.update_application_status(
        db, mahasiswa_nrp, proyek_id, id_pendaftaran, new_status
    )
    if not updated_application:
        raise HTTPException(status_code=404, detail="Application not found or could not be updated")

    # System notification logic could go here after status update
    return updated_application