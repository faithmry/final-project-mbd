# C:\Users\Faith\Downloads\myits-collab\backend\app\services\user_service.py

from sqlalchemy.orm import Session
from app.models import user as user_model
from app.schemas import user as user_schema
from app.core.security import get_password_hash, verify_password

# --- Admin Operations ---

def get_admin_by_id(db: Session, admin_id: str):
    """Fetches an Admin by ID."""
    return db.query(user_model.Admin).filter(user_model.Admin.ID_Admin == admin_id).first()

def get_admin_by_email(db: Session, email: str):
    """Fetches an Admin by email."""
    return db.query(user_model.Admin).filter(user_model.Admin.Email_Admin == email).first()

def create_admin(db: Session, admin: user_schema.AdminCreate):
    """Creates a new Admin in the database."""
    # In a real app, you'd hash the password here before storing
    db_admin = user_model.Admin(
        ID_Admin=admin.id,
        Nama_Admin=admin.nama,
        Email_Admin=admin.email,
        Password_Admin=get_password_hash(admin.password)
    )
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin

# --- Dosen Operations ---

def get_dosen_by_nip(db: Session, nip: str):
    """Fetches a Dosen by NIP."""
    return db.query(user_model.Dosen).filter(user_model.Dosen.NIP == nip).first()

def get_dosen_by_email(db: Session, email: str):
    """Fetches a Dosen by email."""
    return db.query(user_model.Dosen).filter(user_model.Dosen.Email_Dosen == email).first()

def create_dosen(db: Session, dosen: user_schema.DosenCreate):
    """Creates a new Dosen in the database."""
    # In a real app, you'd hash the password here before storing
    db_dosen = user_model.Dosen(
        NIP=dosen.nip,
        Nama_Dosen=dosen.nama,
        Email_Dosen=dosen.email,
        Password_Dosen=get_password_hash(dosen.password)
    )
    db.add(db_dosen)
    db.commit()
    db.refresh(db_dosen)
    return db_dosen

# --- Mahasiswa Operations ---

def get_mahasiswa_by_nrp(db: Session, nrp: str):
    """Fetches a Mahasiswa by NRP."""
    return db.query(user_model.Mahasiswa).filter(user_model.Mahasiswa.NRP == nrp).first()

def get_mahasiswa_by_email(db: Session, email: str):
    """Fetches a Mahasiswa by email."""
    return db.query(user_model.Mahasiswa).filter(user_model.Mahasiswa.Email_Mahasiswa == email).first()

def create_mahasiswa(db: Session, mahasiswa: user_schema.MahasiswaCreate):
    """Creates a new Mahasiswa in the database."""
    # In a real app, you'd hash the password here before storing
    db_mahasiswa = user_model.Mahasiswa(
        NRP=mahasiswa.nrp,
        Nama_Mahasiswa=mahasiswa.nama,
        Email_Mahasiswa=mahasiswa.email,
        Password_Mahasiswa=get_password_hash(mahasiswa.password)
    )
    db.add(db_mahasiswa)
    db.commit()
    db.refresh(db_mahasiswa)
    return db_mahasiswa


def authenticate_user(db: Session, username_or_id: str, password: str):
    user = None
    # Try to find user by ID/NRP/NIP first
    db_admin = get_admin_by_id(db, admin_id=username_or_id)
    if db_admin:
        if verify_password(password, db_admin.Password_Admin):
            user = db_admin
            user.role = "admin" # Add a role attribute for convenience
    if not user:
        db_dosen = get_dosen_by_nip(db, nip=username_or_id)
        if db_dosen:
            if verify_password(password, db_dosen.Password_Dosen):
                user = db_dosen
                user.role = "dosen"
    if not user:
        db_mahasiswa = get_mahasiswa_by_nrp(db, nrp=username_or_id)
        if db_mahasiswa:
            if verify_password(password, db_mahasiswa.Password_Mahasiswa):
                user = db_mahasiswa
                user.role = "mahasiswa"

    # If not found by ID, try by email
    if not user:
        db_admin = get_admin_by_email(db, email=username_or_id)
        if db_admin:
            if verify_password(password, db_admin.Password_Admin):
                user = db_admin
                user.role = "admin"
    if not user:
        db_dosen = get_dosen_by_email(db, email=username_or_id)
        if db_dosen:
            if verify_password(password, db_dosen.Password_Dosen):
                user = db_dosen
                user.role = "dosen"
    if not user:
        db_mahasiswa = get_mahasiswa_by_email(db, email=username_or_id)
        if db_mahasiswa:
            if verify_password(password, db_mahasiswa.Password_Mahasiswa):
                user = db_mahasiswa
                user.role = "mahasiswa"

    return user
# You can add more functions here for updating, deleting, etc.