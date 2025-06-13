# C:\Users\Faith\Downloads\myits-collab\backend\app\models\application.py

from __future__ import annotations
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from app.db.database import Base
import datetime

# --- Dokumen Model (defined first now) ---
class Dokumen(Base):
    __tablename__ = 'Dokumen'

    ID_Dokumen = Column(Integer, primary_key=True, autoincrement=True)
    Nama_Dokumen = Column(String(100), nullable=False)
    File_Path = Column(String(255), nullable=False)
    Tgl_Upload = Column(DateTime, default=datetime.datetime.now)

    Transaksi_Mahasiswa_NRP = Column(String(10), ForeignKey('Transksi_Mahasiswa_Proyek.Mahasiswa_NRP'), nullable=False)
    Transaksi_Proyek_ID_Proyek = Column(String(4), ForeignKey('Transksi_Mahasiswa_Proyek.Proyek_ID_Proyek'), nullable=False)
    Transaksi_ID_Pendaftaran = Column(String(4), ForeignKey('Transksi_Mahasiswa_Proyek.ID_Pendaftaran'), nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ['Transaksi_Mahasiswa_NRP', 'Transaksi_Proyek_ID_Proyek', 'Transaksi_ID_Pendaftaran'],
            ['Transksi_Mahasiswa_Proyek.Mahasiswa_NRP', 'Transksi_Mahasiswa_Proyek.Proyek_ID_Proyek', 'Transksi_Mahasiswa_Proyek.ID_Pendaftaran']
        ),
    )

    # FIX: Add foreign_keys argument to specify the linking columns in THIS (Dokumen) table
    application_transaction = relationship(
        "Transksi_Mahasiswa_Proyek",
        back_populates="documents",
        foreign_keys=[
            Transaksi_Mahasiswa_NRP,
            Transaksi_Proyek_ID_Proyek,
            Transaksi_ID_Pendaftaran
        ]
    )

    def __repr__(self):
        return f"<Dokumen(ID_Dokumen={self.ID_Dokumen}, Nama='{self.Nama_Dokumen}', Path='{self.File_Path}')>"

# --- Transksi_Mahasiswa_Proyek Model (defined second) ---
class Transksi_Mahasiswa_Proyek(Base):
    __tablename__ = 'Transksi_Mahasiswa_Proyek'

    Mahasiswa_NRP = Column(String(10), ForeignKey('Mahasiswa.NRP'), primary_key=True)
    Proyek_ID_Proyek = Column(String(4), ForeignKey('Proyek.ID_Proyek'), primary_key=True)
    ID_Pendaftaran = Column(String(4), primary_key=True, index=True)

    Status = Column(Boolean, nullable=False, default=False)

    mahasiswa = relationship("Mahasiswa")
    proyek = relationship("Proyek", back_populates="applications")

    documents = relationship(
        "Dokumen",
        back_populates="application_transaction",
        foreign_keys=[
            Dokumen.Transaksi_Mahasiswa_NRP,
            Dokumen.Transaksi_Proyek_ID_Proyek,
            Dokumen.Transaksi_ID_Pendaftaran
        ]
    )

    def __repr__(self):
        return f"<Transksi_Mahasiswa_Proyek(NRP='{self.Mahasiswa_NRP}', Proyek_ID='{self.Proyek_ID_Proyek}', ID_Pendaftaran='{self.ID_Pendaftaran}', Status={self.Status})>"