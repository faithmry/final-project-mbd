# C:\Users\Faith\Downloads\myits-collab\backend\app\routers\users.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Union

from app.dependencies import get_current_active_mahasiswa, get_current_active_dosen, get_current_active_admin, get_current_authenticated_user, get_current_active_admin_or_dosen # <--- ENSURE THIS IS HERE
from app.models import user as user_model
from app.db.database import get_db
from app.schemas import projects as project_schema
from app.schemas import applications as application_schema
from app.schemas import user as user_schema
from app.services import projects_service
from app.services import applications_service
# from app.core.security import get_current_active_user # For authentication later
# from app.models import user as user_model # For user types in Depends

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/me/projects/created", response_model=List[project_schema.ProyekResponse])
def get_my_created_projects(
    db: Session = Depends(get_db),
    # FIX: Use the combined dependency we created for Admin OR Dosen
    current_user: user_model.Admin | user_model.Dosen = Depends(get_current_active_admin_or_dosen) # <--- CHANGE THIS LINE!
):
    # The 'current_user_id_or_nip' variable is no longer needed since 'current_user' is now the specific Admin/Dosen object
    # The role check is handled by the dependency itself.

    if isinstance(current_user, user_model.Dosen):
        projects = projects_service.get_all_projects(db, dosen_nip_filter=current_user.NIP)
    elif isinstance(current_user, user_model.Admin):
        projects = projects_service.get_all_projects(db, admin_id_filter=current_user.ID_Admin)
    else:
        # This 'else' branch should now be unreachable due to the Depends()
        raise HTTPException(status_code=403, detail="User role not found for created projects")


    return projects


@router.get("/me/projects/applied", response_model=List[application_schema.ApplicationResponse])
# Requires authentication: current_user: user_model.Mahasiswa = Depends(get_current_active_user)
def get_my_applied_projects(db: Session = Depends(get_db)):
    # Placeholder for getting current user's NRP
    # For now, hardcode for testing
    current_mahasiswa_nrp = "MHS0012345" # Example NRP

    applications = applications_service.get_applications_by_mahasiswa(db, mahasiswa_nrp=current_mahasiswa_nrp)
    return applications


# --- NEW: Endpoint to get current user's profile ---
@router.get("/me", response_model=Union[user_schema.AdminResponse, user_schema.DosenResponse, user_schema.MahasiswaResponse])
def get_current_user_profile(
    current_user: Union[user_model.Admin, user_model.Dosen, user_model.Mahasiswa] = Depends(get_current_authenticated_user)
):
    """
    Returns the profile of the currently authenticated user.
    The response model dynamically adapts based on the user's role.
    """
    return current_user

# Add endpoints for getting user profile details if needed
# @router.get("/me", response_model=user_schema.MahasiswaResponse | user_schema.DosenResponse | user_schema.AdminResponse)
# def get_current_user_profile(current_user: Any = Depends(get_current_active_user)):
#     return current_user