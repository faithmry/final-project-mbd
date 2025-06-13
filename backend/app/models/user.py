# C:\Users\Faith\Downloads\myits-collab\backend\app\models\user.py

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.models.projects import proyek_admin_association
from app.db.database import Base

# Admin Model
class Admin(Base):
    __tablename__ = 'Admin' # Matches SQL table name

    ID_Admin = Column(String(4), primary_key=True, index=True)
    Nama_Admin = Column(String(50), nullable=False)
    Email_Admin = Column(String(50), unique=True, nullable=False)
    Password_Admin = Column(String(255), nullable=False) # Hashing will go here later!

    proyeks_administered = relationship(
        "Proyek",
        secondary=proyek_admin_association,
        back_populates="admins" # This matches the `admins` relationship in the Proyek model
    )

    def __repr__(self):
        return f"<Admin(ID_Admin='{self.ID_Admin}', Nama_Admin='{self.Nama_Admin}')>"

# Dosen (Lecturer) Model
class Dosen(Base):
    __tablename__ = 'Dosen' # Matches SQL table name

    NIP = Column(String(18), primary_key=True, index=True)
    Nama_Dosen = Column(String(50), nullable=False)
    Email_Dosen = Column(String(50), unique=True, nullable=False)
    Password_Dosen = Column(String(255), nullable=False) # Hashing will go here later!

    def __repr__(self):
        return f"<Dosen(NIP='{self.NIP}', Nama_Dosen='{self.Nama_Dosen}')>"

# Mahasiswa (Student) Model
class Mahasiswa(Base):
    __tablename__ = 'Mahasiswa' # Matches SQL table name

    NRP = Column(String(10), primary_key=True, index=True)
    Nama_Mahasiswa = Column(String(50), nullable=False)
    Email_Mahasiswa = Column(String(50), unique=True, nullable=False)
    Password_Mahasiswa = Column(String(255), nullable=False) # Hashing will go here later!

    def __repr__(self):
        return f"<Mahasiswa(NRP='{self.NRP}', Nama_Mahasiswa='{self.Nama_Mahasiswa}')>"