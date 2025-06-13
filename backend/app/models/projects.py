# C:\Users\Faith\Downloads\myits-collab\backend\app\models\project.py

from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Integer, Table
from sqlalchemy.orm import relationship
from app.db.database import Base
import datetime

# Bidang (Field/Area) Model
class Bidang(Base):
    __tablename__ = 'Bidang' # Matches SQL table name

    ID_Bidang = Column(String(4), primary_key=True, index=True)
    Nama_Bidang = Column(String(100), nullable=False, unique=True)

    # Relationship to Proyek (one-to-many: one Bidang can have many Proyek)
    # proyeks = relationship("Proyek", back_populates="bidang")

    def __repr__(self):
        return f"<Bidang(ID_Bidang='{self.ID_Bidang}', Nama_Bidang='{self.Nama_Bidang}')>"

proyek_admin_association = Table(
    'Proyek_Admin', Base.metadata,
    Column('Proyek_ID_Proyek', String(4), ForeignKey('Proyek.ID_Proyek'), primary_key=True),
    Column('Admin_ID_Admin', String(4), ForeignKey('Admin.ID_Admin'), primary_key=True)
)

# Proyek (Project) Model
class Proyek(Base):
    __tablename__ = 'Proyek' # Matches SQL table name

    # ID_Proyek = Column(String(4), primary_key=True, index=True)
    # Judul = Column(String(255), nullable=False)
    # Deskripsi = Column(Text) # LONGTEXT in SQL is typically Text in SQLAlchemy
    # Tgl_Upload = Column(DateTime, default=datetime.datetime.now, nullable=False)
    # Availability = Column(Boolean, nullable=False) # True/False for project availability

    ID_Proyek = Column(String(4), primary_key=True, index=True)
    Judul = Column(String(255), nullable=False)
    Deskripsi = Column(Text, nullable=False)
    Tgl_Upload = Column(DateTime, default=datetime.datetime.now, nullable=False)
    Tgl_Mulai = Column(DateTime, nullable=False)
    Tgl_Selesai = Column(DateTime, nullable=False)
    Bidang = Column(String(500), nullable=False)
    Jumlah_Peserta = Column(Integer, nullable=False)
    Status_Proyek = Column(String(20), nullable=False)
    Availability = Column(Boolean, nullable=False)

    # Foreign Keys
    # Admin_ID_Admin = Column(String(4), ForeignKey('Admin.ID_Admin'), nullable=True)
    Dosen_NIP = Column(String(18), ForeignKey('Dosen.NIP'), nullable=True)
    # Nama_Bidang = Column(String(100), nullable=False) # Changed from Bidang_ID_Bidang to Nama_Bidang, String(100)
    # Bidang_ID_Bidang = Column(String(4), ForeignKey('Bidang.ID_Bidang'), nullable=False) # Corrected to String(4)

    # Relationships (to access related objects via model instances)
    # admin = relationship("Admin") # One-to-one or Many-to-one to Admin
    dosen = relationship("Dosen") # One-to-one or Many-to-one to Dosen
    # bidang = relationship("Bidang", back_populates="proyeks") # Many-to-one to Bidang
    
    admins = relationship(
        "Admin",
        secondary=proyek_admin_association, # Use the Table object here
        back_populates="proyeks_administered" # This backref needs to be defined in Admin model
    )    

    # Relationship to Transksi_Mahasiswa_Proyek (one-to-many: one Proyek can have many applications)
    applications = relationship("Transksi_Mahasiswa_Proyek", back_populates="proyek")

    def __repr__(self):
        return f"<Proyek(ID_Proyek='{self.ID_Proyek}', Judul='{self.Judul}')>"