# C:\Users\Faith\Downloads\myits-collab\backend\app\services\project_service.py

from sqlalchemy.orm import Session, joinedload
from app.models import projects as project_model
from app.schemas import projects as project_schema
from app.models import user as user_model # Import user models to fetch Admin
from sqlalchemy import or_ # Added for clarity if needed in future filters
from typing import List, Optional
import datetime
import uuid

# --- Helper function for generating unique IDs ---
def generate_unique_id(prefix: str, db: Session, model, id_column, length: int) -> str:
    """Generates a unique ID of specified length with a prefix."""
    while True:
        # Generate random hex and take required length after prefix
        unique_part = uuid.uuid4().hex[:length - len(prefix)].upper()
        new_id = f"{prefix}{unique_part}"
        
        # Check if this ID already exists in the database for the given model and ID column
        existing_item = db.query(model).filter(id_column == new_id).first()
        if not existing_item:
            return new_id

# --- Bidang Operations ---

def get_bidang_by_id(db: Session, bidang_id: str):
    """Fetches a Bidang by ID."""
    return db.query(project_model.Bidang).filter(project_model.Bidang.ID_Bidang == bidang_id).first()

def get_all_bidang(db: Session) -> List[project_model.Bidang]:
    """Fetches all Bidang entries."""
    return db.query(project_model.Bidang).all()

def create_bidang(db: Session, bidang: project_schema.BidangCreate):
    """Creates a new Bidang in the database."""
    db_bidang = project_model.Bidang(
        ID_Bidang=bidang.id_bidang,
        Nama_Bidang=bidang.nama_bidang
    )
    db.add(db_bidang)
    db.commit()
    db.refresh(db_bidang)
    return db_bidang

# --- Proyek Operations ---

def get_project_by_id(db: Session, project_id: str):
    """Fetches a project by ID."""
    # Use joinedload to eager-load related data (admin, dosen, bidang)
    # This avoids N+1 query problem when you access relationships
    return db.query(project_model.Proyek).options(
        # joinedload(project_model.Proyek.admin),
        joinedload(project_model.Proyek.admins),
        joinedload(project_model.Proyek.dosen),
        # joinedload(project_model.Proyek.bidang)
    ).filter(project_model.Proyek.ID_Proyek == project_id).first()

def get_all_projects(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    available_only: Optional[bool] = None,
    dosen_nip_filter: Optional[str] = None, # <--- ADD THIS ARGUMENT
    admin_id_filter: Optional[str] = None  # <--- ADD THIS ARGUMENT
) -> List[project_model.Proyek]:
    """Fetches a list of projects with optional filtering."""
    query = db.query(project_model.Proyek).options(
        # joinedload(project_model.Proyek.admin),
        joinedload(project_model.Proyek.admins),
        joinedload(project_model.Proyek.dosen),
        # joinedload(project_model.Proyek.bidang)
    )
    if available_only is not None:
        query = query.filter(project_model.Proyek.Availability == available_only)

    if dosen_nip_filter: # <--- APPLY FILTER IF PROVIDED
        query = query.filter(project_model.Proyek.Dosen_NIP == dosen_nip_filter)
    if admin_id_filter: # <--- APPLY FILTER IF PROVIDED
        query = query.filter(project_model.Proyek.Admin_ID_Admin == admin_id_filter)    
        
    query = query.options(
        joinedload(project_model.Proyek.dosen), # Direct relationship
        joinedload(project_model.Proyek.admins), # Many-to-many relationship
    )        

    return query.offset(skip).limit(limit).all()

def create_project(db: Session, project: project_schema.ProyekCreate, admin_id: Optional[str] = None, dosen_nip: Optional[str] = None):
    """Creates a new project in the database."""

    # Generate a unique ID_Proyek (4 characters)
    # Loop to ensure uniqueness, though highly unlikely to collide with 4 hex chars from UUID
    while True:
        new_id_proyek = str(uuid.uuid4().hex)[:4].upper() # e.g., 'A1B2'
        # Check if this ID already exists in the database
        existing_project = db.query(project_model.Proyek).filter(
            project_model.Proyek.ID_Proyek == new_id_proyek
        ).first()
        if not existing_project:
            break # Found a unique ID

    project_data = project.model_dump()
    
    # --- Map Pydantic (lowercase) field names to SQLAlchemy (uppercase) attribute names ---
    # Create a new dictionary with keys matching SQLAlchemy model attributes
    model_attrs = {
        "ID_Proyek": new_id_proyek, 
        "Judul": project_data["judul"],
        "Deskripsi": project_data["deskripsi"],
        "Bidang": project_data["bidang"],
        "Jumlah_Peserta": project_data.get("jumlah_peserta") or 1, # Use .get() and apply default here
        "Status_Proyek": project_data.get("status_proyek") or "Open", # Use .get() and apply default here
        "Availability": project_data["availability"],
        "Tgl_Mulai": project_data.get("tgl_mulai") or datetime.datetime.now(), # Use .get() and apply default here
        "Tgl_Selesai": project_data.get("tgl_selesai") or (
                       (project_data.get("tgl_mulai") or datetime.datetime.now()) + datetime.timedelta(days=30)
                       ), # Use .get() and apply default here
        "Tgl_Upload": datetime.datetime.now(), # Always set by backend
        "Dosen_NIP": dosen_nip # Passed explicitly
    }
    
    # --- Ensure `Tgl_Selesai` is correctly calculated if `Tgl_Mulai` was defaulted ---
    # This recalculates Tgl_Selesai if Tgl_Mulai was also defaulted to now()
    if 'Tgl_Selesai' in project_data and project_data['Tgl_Selesai'] is None:
        model_attrs['Tgl_Selesai'] = model_attrs['Tgl_Mulai'] + datetime.timedelta(days=30)

    # Instantiate the Proyek model with the correctly mapped attributes
    db_project = project_model.Proyek(**model_attrs)
    
    db.add(db_project)
    if admin_id:
        # If admin_id is provided, add the Admin to the project
        admin = db.query(user_model.Admin).filter(user_model.Admin.ID_Admin == admin_id).first()
        if admin:
            db_project.admins.append(admin) # Append to many-to-many relationship    
    db.commit()
    db.refresh(db_project)
    return db_project

def update_project(db: Session, db_project: project_model.Proyek, project_update: project_schema.ProyekUpdate):
    """Updates an existing project."""
    update_data = project_update.model_dump(exclude_unset=True) # Exclude fields not set in the update request

    for key, value in update_data.items():
        # if key == 'bidang_id': # Special handling for FK if you want to update via alias
        #     setattr(db_project, 'Bidang_ID_Bidang', value)
        # else:
        setattr(db_project, key, value) # Directly set attributes from Pydantic schema

    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def delete_project(db: Session, project_id: str):
    """Deletes a project."""
    db_project = db.query(project_model.Proyek).filter(project_model.Proyek.ID_Proyek == project_id).first()
    if db_project:
        db.delete(db_project)
        db.commit()
        return True
    return False

# You can add more functions here for updating, deleting, filtering, etc.