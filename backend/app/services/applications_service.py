# C:\Users\Faith\Downloads\myits-collab\backend\app\services\applications_service.py

from sqlalchemy.orm import Session, joinedload
from app.models import applications as application_model
from app.models import projects as project_model # Need project model to check existence
from app.models import user as user_model # Need user model to check existence
from app.schemas import applications as application_schema
from app.schemas import user as user_schema # For nested response schemas
from typing import List, Optional
import uuid # For generating unique IDs for ID_Pendaftaran and potentially ID_Proyek
import datetime


def get_application_by_id(
    db: Session,
    mahasiswa_nrp: str,
    proyek_id: str,
    id_pendaftaran: str
):
    """Fetches a specific application by its composite primary key."""
    return db.query(application_model.Transksi_Mahasiswa_Proyek).filter(
        application_model.Transksi_Mahasiswa_Proyek.Mahasiswa_NRP == mahasiswa_nrp,
        application_model.Transksi_Mahasiswa_Proyek.Proyek_ID_Proyek == proyek_id,
        application_model.Transksi_Mahasiswa_Proyek.ID_Pendaftaran == id_pendaftaran
    ).options(
        joinedload(application_model.Transksi_Mahasiswa_Proyek.documents),
        joinedload(application_model.Transksi_Mahasiswa_Proyek.mahasiswa),
        joinedload(application_model.Transksi_Mahasiswa_Proyek.proyek)
    ).first()

def get_applications_for_project(db: Session, project_id: str) -> List[application_model.Transksi_Mahasiswa_Proyek]:
    """Fetches all applications for a given project."""
    return db.query(application_model.Transksi_Mahasiswa_Proyek).filter(
        application_model.Transksi_Mahasiswa_Proyek.Proyek_ID_Proyek == project_id
    ).options(
        joinedload(application_model.Transksi_Mahasiswa_Proyek.mahasiswa),
        joinedload(application_model.Transksi_Mahasiswa_Proyek.documents)
    ).all()

def get_applications_by_mahasiswa(db: Session, mahasiswa_nrp: str) -> List[application_model.Transksi_Mahasiswa_Proyek]:
    """Fetches all applications made by a specific student."""
    return db.query(application_model.Transksi_Mahasiswa_Proyek).filter(
        application_model.Transksi_Mahasiswa_Proyek.Mahasiswa_NRP == mahasiswa_nrp
    ).options(
        joinedload(application_model.Transksi_Mahasiswa_Proyek.proyek),
        joinedload(application_model.Transksi_Mahasiswa_Proyek.documents)
    ).all()


def apply_to_project(
    db: Session,
    mahasiswa_nrp: str,
    project_id: str,
    cv_file_path: Optional[str] = None # Path to the uploaded CV file
) -> application_model.Transksi_Mahasiswa_Proyek:
    """Handles a student applying to a project, including optional CV upload."""

    # 1. Check if student and project exist
    student = user_model.Mahasiswa # Replace with actual lookup
    project = project_model.Proyek # Replace with actual lookup
    # In a real scenario, you'd fetch these from the DB:
    # student = db.query(user_model.Mahasiswa).filter(user_model.Mahasiswa.NRP == mahasiswa_nrp).first()
    # project = db.query(project_model.Proyek).filter(project_model.Proyek.ID_Proyek == project_id).first()
    # if not student or not project:
    #     raise ValueError("Student or Project not found.")

    # 2. Check if student already applied to this project (optional, depends on if multiple applications are allowed)
    # This application design allows multiple applications with different ID_Pendaftaran
    # If you want to restrict to one application per student per project:
    # existing_app = db.query(application_model.Transksi_Mahasiswa_Proyek).filter(
    #     application_model.Transksi_Mahasiswa_Proyek.Mahasiswa_NRP == mahasiswa_nrp,
    #     application_model.Transksi_Mahasiswa_Proyek.Proyek_ID_Proyek == project_id
    # ).first()
    # if existing_app:
    #     raise ValueError("Student has already applied to this project.")


    # 3. Generate a unique ID_Pendaftaran
    # Assuming ID_Pendaftaran is CHAR(4), you'll need a short unique generator
    # For robust unique IDs, use a proper UUID and truncate/hash if needed.
    # For now, let's use a truncated UUID.
    id_pendaftaran = str(uuid.uuid4().hex)[:4].upper() # Example: 'A1B2'
    # Ensure it's unique (loop if necessary, though collision risk is low for 4 chars with UUID)
    while db.query(application_model.Transksi_Mahasiswa_Proyek).filter(
        application_model.Transksi_Mahasiswa_Proyek.Mahasiswa_NRP == mahasiswa_nrp,
        application_model.Transksi_Mahasiswa_Proyek.Proyek_ID_Proyek == project_id,
        application_model.Transksi_Mahasiswa_Proyek.ID_Pendaftaran == id_pendaftaran
    ).first():
        id_pendaftaran = str(uuid.uuid4().hex)[:4].upper()


    # 4. Create the application transaction
    db_application = application_model.Transksi_Mahasiswa_Proyek(
        Mahasiswa_NRP=mahasiswa_nrp,
        Proyek_ID_Proyek=project_id,
        ID_Pendaftaran=id_pendaftaran,
        Status=False # Default to pending
    )
    db.add(db_application)
    db.flush() # Use flush to get the ID_Pendaftaran before commit if needed by documents

    # 5. Create the Dokumen entry if CV path is provided
    if cv_file_path:
        db_document = application_model.Dokumen(
            Transaksi_Mahasiswa_NRP=mahasiswa_nrp,
            Transaksi_Proyek_ID_Proyek=project_id,
            Transaksi_ID_Pendaftaran=id_pendaftaran,
            Nama_Dokumen="Curriculum Vitae",
            File_Path=cv_file_path,
            Tgl_Upload=datetime.datetime.now()
        )
        db.add(db_document)

    db.commit()
    db.refresh(db_application)
    return db_application

def update_application_status(
    db: Session,
    mahasiswa_nrp: str,
    proyek_id: str,
    id_pendaftaran: str,
    new_status: bool
):
    """Updates the status of a specific application."""
    db_application = get_application_by_id(db, mahasiswa_nrp, proyek_id, id_pendaftaran)
    if db_application:
        db_application.Status = new_status
        db.commit()
        db.refresh(db_application)
        return db_application
    return None

# Add more functions as needed (e.g., delete application, get documents for an application)