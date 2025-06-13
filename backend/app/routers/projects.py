# C:\Users\Faith\Downloads\myits-collab\backend\app\routers\projects.py

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form # Add File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List, Optional, Union # Add Union for type hints

from app.db.database import get_db
from app.schemas import projects as project_schema
from app.services import projects_service
from app.services import applications_service # Import the applications service
from app.dependencies import get_current_active_admin, get_current_active_dosen, get_current_active_mahasiswa, get_current_authenticated_user ,get_current_active_admin_or_dosen# Import security dependencies
from app.models import user as user_model # Import user models for type hints

import os # For file path operations
import uuid # For generating unique filenames

# Define the upload directory. Consider putting this in app/core/config.py for production.
# This path is relative to where uvicorn is run (the 'backend' folder)
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads", "cvs")


router = APIRouter(
    prefix="/projects",
    tags=["Projects"]
)

# --- Endpoint for Creating Projects ---
@router.post("/", response_model=project_schema.ProyekResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project: project_schema.ProyekCreate,
    db: Session = Depends(get_db),
    # Use the new combined dependency
    current_user: Union[user_model.Admin, user_model.Dosen] = Depends(get_current_active_admin_or_dosen) # <--- CHANGE THIS LINE!
):
    # Dynamically get the uploader ID based on the authenticated user's role
    admin_id = None
    dosen_nip = None

    if isinstance(current_user, user_model.Admin):
        admin_id = current_user.ID_Admin
    elif isinstance(current_user, user_model.Dosen):
        dosen_nip = current_user.NIP
    # The 'else' case and 403 HTTPException are now handled by the dependency itself.

    created_project = projects_service.create_project(
        db=db,
        project=project,
        admin_id=admin_id,
        dosen_nip=dosen_nip
    )
    return created_project

# --- Endpoint for Reading All Projects ---
@router.get("/", response_model=List[project_schema.ProyekResponse])
def read_projects(
    skip: int = 0,
    limit: int = 100,
    available_only: Optional[bool] = None,
    db: Session = Depends(get_db),
    # Projects can be read by any authenticated user (or even public if desired, by removing Depends)
    current_user: Union[user_model.Mahasiswa, user_model.Dosen, user_model.Admin] = Depends(get_current_authenticated_user)
):
    projects = projects_service.get_all_projects(db, skip=skip, limit=limit, available_only=available_only)
    return projects

# --- Endpoint for Reading Project Details ---
@router.get("/{project_id}", response_model=project_schema.ProyekDetailResponse)
def read_project_details(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: Union[user_model.Mahasiswa, user_model.Dosen, user_model.Admin] = Depends(get_current_authenticated_user)
):
    db_project = projects_service.get_project_by_id(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    # Here you can implement the "different for uploader and user" logic
    # For a Dosen/Admin who is the uploader, or a general Admin, show applicants
    is_uploader = (isinstance(current_user, user_model.Admin) and current_user.ID_Admin == db_project.Admin_ID_Admin) or \
                  (isinstance(current_user, user_model.Dosen) and current_user.NIP == db_project.Dosen_NIP)
    is_overall_admin = isinstance(current_user, user_model.Admin)

    if is_uploader or is_overall_admin:
        # Fetch applicants and attach them. Ensure ProyekDetailResponse schema can handle 'applicants'
        db_project.applicants = applications_service.get_applications_for_project(db, project_id)
        # Pydantic will auto-convert relationships with `from_attributes=True` in ProyekDetailResponse
    else:
        # For general users (e.g., Mahasiswa), clear the applicants list if it was eager loaded
        # Or, ideally, have a separate response model for non-uploader view.
        # For simplicity now, we ensure 'applicants' field in schema is Optional or List[].
        pass # The db_project object's .applicants will be empty if not explicitly set above

    return db_project

# --- Endpoint for Updating Project Details ---
@router.put("/{project_id}", response_model=project_schema.ProyekResponse)
def update_project(
    project_id: str,
    project_update: project_schema.ProyekUpdate,
    db: Session = Depends(get_db),
    current_user: Union[user_model.Admin, user_model.Dosen] = Depends(get_current_active_admin or get_current_active_dosen)
):
    db_project = projects_service.get_project_by_id(db, project_id=project_id)
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    # Authorization check: ensure current user is the uploader or an overall admin
    is_uploader = (isinstance(current_user, user_model.Admin) and current_user.ID_Admin == db_project.Admin_ID_Admin) or \
                  (isinstance(current_user, user_model.Dosen) and current_user.NIP == db_project.Dosen_NIP)
    is_overall_admin = isinstance(current_user, user_model.Admin)

    if not (is_uploader or is_overall_admin):
        raise HTTPException(status_code=403, detail="Not authorized to update this project")

    updated_project = projects_service.update_project(db, db_project, project_update)
    return updated_project

# --- NEW: Endpoint for listing all Bidang ---
@router.get("/bidangs", response_model=List[project_schema.BidangResponse], tags=["Projects"])
def read_all_bidangs(db: Session = Depends(get_db)):
    # This calls the service function you already created in projects_service.py
    bidangs = projects_service.get_all_bidang(db)
    return bidangs

# --- NEW: Endpoint for Applying to a Project with CV Upload ---
@router.post("/{project_id}/apply", status_code=status.HTTP_201_CREATED)
def apply_to_project(
    project_id: str,
    # This parameter receives the uploaded file.
    # Frontend will send this as multipart/form-data.
    cv_file: UploadFile = File(...),
    # If you need other form fields, e.g., a short motivation letter:
    # motivation_letter: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: user_model.Mahasiswa = Depends(get_current_active_mahasiswa) # Only authenticated Mahasiswa
):
    # Ensure the upload directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Generate a unique filename to prevent overwrites and provide traceability
    file_extension = os.path.splitext(cv_file.filename)[1] # Get original file extension
    # Example: MHS0024_PRJ1_uniquehash.pdf
    unique_filename = f"{current_user.NRP}_{project_id}_{uuid.uuid4().hex}{file_extension}"
    file_location = os.path.join(UPLOAD_DIR, unique_filename)

    try:
        # Read the file content and write it to the specified location
        with open(file_location, "wb+") as file_object:
            file_object.write(cv_file.file.read())
    except Exception as e:
        # Log the actual error for debugging
        print(f"Error saving file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file. Error: {e}")

    # Call the service to create the application and document entry
    try:
        created_application = applications_service.apply_to_project(
            db=db,
            mahasiswa_nrp=current_user.NRP, # Get NRP from the authenticated user
            project_id=project_id,
            cv_file_path=file_location # Pass the path where the file is saved
        )
    except ValueError as e:
        # For known business rule errors (e.g., already applied)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Catch broader exceptions during service call for debugging
        print(f"Error in applications_service.apply_to_project: {e}")
        raise HTTPException(status_code=500, detail=f"Application submission failed due to internal error. Error: {e}")

    return {
        "message": "Application submitted successfully",
        "id_pendaftaran": created_application.ID_Pendaftaran,
        "file_path": file_location
    }