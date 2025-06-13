# C:\Users\Faith\Downloads\myits-collab\backend\app\routers\auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm # Add OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas import user as user_schema
from app.services import user_service
from app.core.security import create_access_token # Import this

# Assuming you'll add security later, import placeholders for now
# from app.core.security import get_password_hash, verify_password, create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/register/mahasiswa", response_model=user_schema.MahasiswaResponse, status_code=status.HTTP_201_CREATED)
def register_mahasiswa(mahasiswa: user_schema.MahasiswaCreate, db: Session = Depends(get_db)):
    db_mahasiswa = user_service.get_mahasiswa_by_email(db, email=mahasiswa.email)
    if db_mahasiswa:
        raise HTTPException(status_code=400, detail="Email already registered")

    # In a real app: hashed_password = get_password_hash(mahasiswa.password)
    # mahasiswa.password = hashed_password # Update schema to store hash

    return user_service.create_mahasiswa(db=db, mahasiswa=mahasiswa)

@router.post("/register/dosen", response_model=user_schema.DosenResponse, status_code=status.HTTP_201_CREATED)
def register_dosen(dosen: user_schema.DosenCreate, db: Session = Depends(get_db)):
    db_dosen = user_service.get_dosen_by_email(db, email=dosen.email)
    if db_dosen:
        raise HTTPException(status_code=400, detail="Email already registered")

    # In a real app: hashed_password = get_password_hash(dosen.password)
    # dosen.password = hashed_password # Update schema to store hash

    return user_service.create_dosen(db=db, dosen=dosen)

@router.post("/login")
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = user_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # The 'sub' (subject) in the JWT payload should be a unique identifier for the user.
    # We need to pick the correct ID based on the user's role.
    if user.role == "mahasiswa":
        user_identifier = user.NRP
    elif user.role == "dosen":
        user_identifier = user.NIP
    elif user.role == "admin":
        user_identifier = user.ID_Admin
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Invalid user role")

    # Create access token
    access_token = create_access_token(
        data={"sub": user_identifier, "role": user.role}
    )
    return {"access_token": access_token, "token_type": "bearer", "user_role": user.role}