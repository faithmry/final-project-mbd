# C:\Users\Faith\Downloads\myits-collab\backend\app\schemas\user.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional # Add this if you use Optional for fields

# --- Input Schemas ---
# These schemas define the expected structure for incoming request bodies.
# They can use aliases to map frontend friendly names (e.g., 'nama') to backend/DB names (e.g., 'Nama_')

class UserBase(BaseModel):
    # These fields are used for input (Create schemas) where the alias matches the expected JSON key
    nama: str = Field(..., max_length=50, alias="Nama_")
    email: EmailStr = Field(..., alias="Email_")

class AdminCreate(UserBase):
    id: str = Field(..., max_length=4, alias="ID_Admin")
    password: str = Field(..., min_length=6, alias="Password_Admin")

class DosenCreate(UserBase):
    nip: str = Field(..., max_length=18, alias="NIP")
    password: str = Field(..., min_length=6, alias="Password_Dosen")

class MahasiswaCreate(UserBase):
    nrp: str = Field(..., max_length=10, alias="NRP")
    password: str = Field(..., min_length=6, alias="Password_Mahasiswa")

# Schema for authentication (login)
class UserLogin(BaseModel):
    username_or_id: str = Field(..., alias="UsernameOrID") # Can be NRP, NIP, or ID_Admin, or email
    password: str = Field(..., alias="Password")

# --- Output Schemas ---
# These schemas define the structure of data returned by the API.
# When `from_attributes = True` is used, Pydantic maps fields from ORM models.
# The Pydantic field names here should match the *attribute names on your SQLAlchemy models*.
# If you want a different key name in the final JSON response, use `alias`.

class AdminResponse(BaseModel):
    # Pydantic field name should match SQLAlchemy model's attribute name (e.g., ID_Admin)
    ID_Admin: str = Field(..., alias="ID_Admin") # Alias makes the JSON key "ID_Admin"
    Nama_Admin: str = Field(..., alias="Nama_Admin") # Alias makes the JSON key "Nama_Admin"
    Email_Admin: EmailStr = Field(..., alias="Email_Admin") # Alias makes the JSON key "Email_Admin"
    # Note: Password_Admin is not included for security

    class Config:
        from_attributes = True # Enable ORM mode for Pydantic v2
        populate_by_name = True # Allow mapping by alias

class DosenResponse(BaseModel):
    NIP: str = Field(..., alias="NIP")
    Nama_Dosen: str = Field(..., alias="Nama_Dosen")
    Email_Dosen: EmailStr = Field(..., alias="Email_Dosen")

    class Config:
        from_attributes = True
        populate_by_name = True

class MahasiswaResponse(BaseModel):
    NRP: str = Field(..., alias="NRP")
    Nama_Mahasiswa: str = Field(..., alias="Nama_Mahasiswa") # Match SQLAlchemy attribute name 'Nama_Mahasiswa'
    Email_Mahasiswa: EmailStr = Field(..., alias="Email_Mahasiswa") # Match SQLAlchemy attribute name 'Email_Mahasiswa'

    class Config:
        from_attributes = True
        populate_by_name = True

# For the ProyekDetailResponse in app/schemas/projects.py, if you import these,
# they should now reference these `*Response` classes directly.