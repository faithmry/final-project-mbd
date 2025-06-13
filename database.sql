-- tables
-- Table: Admin
CREATE TABLE Admin (
    ID_Admin char(4)  NOT NULL,
    Nama_Admin varchar(255)  NOT NULL,
    Email_Admin varchar(255)  NOT NULL,
    Password_Admin varchar(255)  NOT NULL,
    CONSTRAINT Admin_pk PRIMARY KEY (ID_Admin)
);

-- Table: Dokumen
CREATE TABLE Dokumen (
    ID_Dokumen char(4)  NOT NULL,
    Nama_Dokumen varchar(255)  NOT NULL,
    File_Path varchar(255)  NOT NULL,
    Tgl_Upload datetime  NOT NULL,
    Transaksi_ID_Transaksi char(4)  NOT NULL,
    CONSTRAINT Dokumen_pk PRIMARY KEY (ID_Dokumen)
);

-- Table: Dosen
CREATE TABLE Dosen (
    NIP char(18)  NOT NULL,
    Nama_Dosen varchar(255)  NOT NULL,
    Email_Dosen varchar(255)  NOT NULL,
    Password_Dosen varchar(255)  NOT NULL,
    Dept_Dosen varchar(255)  NOT NULL,
    CONSTRAINT Dosen_pk PRIMARY KEY (NIP)
);

-- Table: Mahasiswa
CREATE TABLE Mahasiswa (
    NRP char(10)  NOT NULL,
    Nama_Mahasiswa varchar(255)  NOT NULL,
    Email_Mahasiswa varchar(255)  NOT NULL,
    Password_Mahasiswa varchar(255)  NOT NULL,
    Dept_Mahasiswa varchar(255)  NOT NULL,
    CONSTRAINT Mahasiswa_pk PRIMARY KEY (NRP)
);

-- Table: Proyek
CREATE TABLE Proyek (
    ID_Proyek char(4)  NOT NULL,
    Judul varchar(255)  NOT NULL,
    Deskripsi longtext  NOT NULL,
    Tgl_Upload datetime  NOT NULL,
    Tgl_Mulai datetime  NOT NULL,
    Tgl_Selesai datetime  NOT NULL,
    Bidang varchar(500)  NOT NULL,
    Jumlah_Peserta int  NOT NULL,
    Status_Proyek varchar(20)  NOT NULL,
    Availability bool  NOT NULL,
    Dosen_NIP char(18)  NULL,
    CONSTRAINT Proyek_pk PRIMARY KEY (ID_Proyek)
);

-- Table: Proyek_Admin
CREATE TABLE Proyek_Admin (
    Proyek_ID_Proyek char(4)  NOT NULL,
    Admin_ID_Admin char(4)  NOT NULL,
    CONSTRAINT Proyek_Admin_pk PRIMARY KEY (Proyek_ID_Proyek,Admin_ID_Admin)
);

-- Table: Transaksi
CREATE TABLE Transaksi_Mahasiswa_Proyek (
    ID_Transaksi char(4)  NOT NULL,
    Status_Transaksi varchar(20)  NOT NULL,
    Role varchar(20)  NOT NULL,
    Proyek_ID_Proyek char(4)  NOT NULL,
    Mahasiswa_NRP char(10)  NOT NULL,
    CONSTRAINT Transaksi_pk PRIMARY KEY (ID_Transaksi)
);

-- foreign keys
-- Reference: Dokumen_Transaksi (table: Dokumen)
ALTER TABLE Dokumen ADD CONSTRAINT Dokumen_Transaksi FOREIGN KEY Dokumen_Transaksi (Transaksi_ID_Transaksi)
    REFERENCES Transaksi_Mahasiswa_Proyek (ID_Transaksi);

-- Reference: Proyek_Admin_Admin (table: Proyek_Admin)
ALTER TABLE Proyek_Admin ADD CONSTRAINT Proyek_Admin_Admin FOREIGN KEY Proyek_Admin_Admin (Admin_ID_Admin)
    REFERENCES Admin (ID_Admin);

-- Reference: Proyek_Admin_Proyek (table: Proyek_Admin)
ALTER TABLE Proyek_Admin ADD CONSTRAINT Proyek_Admin_Proyek FOREIGN KEY Proyek_Admin_Proyek (Proyek_ID_Proyek)
    REFERENCES Proyek (ID_Proyek);

-- Reference: Proyek_Dosen (table: Proyek)
ALTER TABLE Proyek ADD CONSTRAINT Proyek_Dosen FOREIGN KEY Proyek_Dosen (Dosen_NIP)
    REFERENCES Dosen (NIP);

-- Reference: Transaksi_Mahasiswa (table: Transaksi_Mahasiswa_Proyek)
ALTER TABLE Transaksi_Mahasiswa_Proyek ADD CONSTRAINT Transaksi_Mahasiswa FOREIGN KEY Transaksi_Mahasiswa (Mahasiswa_NRP)
    REFERENCES Mahasiswa (NRP);

-- Reference: Transaksi_Proyek (table: Transaksi_Mahasiswa_Proyek)
ALTER TABLE Transaksi_Mahasiswa_Proyek ADD CONSTRAINT Transaksi_Proyek FOREIGN KEY Transaksi_Proyek (Proyek_ID_Proyek)
    REFERENCES Proyek (ID_Proyek);

-- End of file.

