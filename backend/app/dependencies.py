# C:\Users\Faith\Downloads\myits-collab\backend\app\dependencies.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Annotated, Union

from app.core.security import decode_access_token
from app.db.database import get_db
from app.models import user as user_model # Import your user models

# OAuth2PasswordBearer is a FastAPI utility for handling token authentication
# The 'tokenUrl' points to your login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Function to get the current authenticated user from the token
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id_or_nip = payload.get("sub")
    user_role = payload.get("role")

    if user_id_or_nip is None or user_role is None:
        raise credentials_exception

    # Fetch the user based on their role
    if user_role == "mahasiswa":
        user = db.query(user_model.Mahasiswa).filter(user_model.Mahasiswa.NRP == user_id_or_nip).first()
    elif user_role == "dosen":
        user = db.query(user_model.Dosen).filter(user_model.Dosen.NIP == user_id_or_nip).first()
    elif user_role == "admin":
        user = db.query(user_model.Admin).filter(user_model.Admin.ID_Admin == user_id_or_nip).first()
    else:
        raise credentials_exception # Invalid role in token

    if user is None:
        raise credentials_exception # User not found in DB

    return user

# Dependencies to get current active user by role
def get_current_active_mahasiswa(current_user: Annotated[user_model.Mahasiswa, Depends(get_current_user)]):
    if not isinstance(current_user, user_model.Mahasiswa):
        raise HTTPException(status_code=403, detail="Not a student user")
    return current_user

def get_current_active_dosen(current_user: Annotated[user_model.Dosen, Depends(get_current_user)]):
    if not isinstance(current_user, user_model.Dosen):
        raise HTTPException(status_code=403, detail="Not a lecturer user")
    return current_user

def get_current_active_admin(current_user: Annotated[user_model.Admin, Depends(get_current_user)]):
    if not isinstance(current_user, user_model.Admin):
        raise HTTPException(status_code=403, detail="Not an admin user")
    return current_user

# For any authenticated user (e.g., to view dashboard)
def get_current_authenticated_user(current_user: Annotated[Union[user_model.Mahasiswa, user_model.Dosen, user_model.Admin], Depends(get_current_user)]):
    return current_user

def get_current_active_admin_or_dosen(
    current_user: Annotated[
        Union[user_model.Admin, user_model.Dosen, user_model.Mahasiswa], # Use Union for all possible user types
        Depends(get_current_authenticated_user) # Get any authenticated user
    ]
):
    if not isinstance(current_user, (user_model.Admin, user_model.Dosen)):
        raise HTTPException(status_code=403, detail="Not authorized. Must be an Admin or Dosen user.")
    return current_user