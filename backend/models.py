# hms_backend/models.py
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class User(Base):
    """
    SQLAlchemy ORM model for a User.
    Represents the 'users' table for authentication.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    # Define roles: admin, doctor, nurse, receptionist, patient, pharmacist
    role = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

class Patient(Base):
    """
    SQLAlchemy ORM model for a Patient.
    Represents the 'patients' table in the database.
    """
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String)
    date_of_birth = Column(Date)
    address = Column(String)
    gender = Column(String)

    # Relationships
    # A patient can have multiple appointments
    appointments = relationship("Appointment", back_populates="patient")
    # A patient can have multiple visit records (EHR)
    patient_visits = relationship("PatientVisit", back_populates="patient")

class Doctor(Base):
    """
    SQLAlchemy ORM model for a Doctor.
    Represents the 'doctors' table in the database.
    """
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String)
    specialization = Column(String)
    license_number = Column(String, unique=True, index=True)

    # Relationships
    # A doctor can have multiple appointments
    appointments = relationship("Appointment", back_populates="doctor")
    # A doctor can have multiple patient visit records (EHR)
    patient_visits = relationship("PatientVisit", back_populates="doctor")

class Appointment(Base):
    """
    SQLAlchemy ORM model for an Appointment.
    Represents the 'appointments' table in the database.
    """
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), index=True)
    appointment_time = Column(DateTime, default=datetime.utcnow) # Store UTC time
    reason = Column(String)
    status = Column(String, default="Scheduled") # e.g., Scheduled, Completed, Cancelled

    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")

class PatientVisit(Base):
    """
    SQLAlchemy ORM model for a Patient Visit record (EHR/EMR).
    This represents the "single appointment form" for patient status.
    """
    __tablename__ = "patient_visits"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), index=True, nullable=True) # Doctor might not always be assigned
    visit_date = Column(DateTime, default=datetime.utcnow) # Date and time of the visit/record entry

    # Clinical Notes / Chief Complaint
    chief_complaint = Column(Text, nullable=True)
    clinical_notes = Column(Text, nullable=True)

    # Vital Signs
    blood_pressure = Column(String, nullable=True) # e.g., "120/80"
    temperature = Column(String, nullable=True)    # e.g., "98.6 F"
    pulse_rate = Column(Integer, nullable=True)
    respiration_rate = Column(Integer, nullable=True)
    weight_kg = Column(String, nullable=True)
    height_cm = Column(String, nullable=True)

    # Diagnosis
    diagnosis = Column(Text, nullable=True) # ICD-10 codes could be integrated later

    # Treatment / Procedures
    treatment = Column(Text, nullable=True)
    procedures_performed = Column(Text, nullable=True)

    # Prescriptions (simple text for now, could be a separate table later)
    prescriptions = Column(Text, nullable=True)

    # Follow-up
    follow_up_instructions = Column(Text, nullable=True)
    next_appointment_date = Column(Date, nullable=True)

    # Relationships
    patient = relationship("Patient", back_populates="patient_visits")
    doctor = relationship("Doctor", back_populates="patient_visits")

# --- Placeholder for other modules (future expansion) ---
# class Drug(Base):
#     __tablename__ = "drugs"
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, unique=True)
#     stock_quantity = Column(Integer)
#     expiry_date = Column(Date)
#     # ... other drug details

# class Prescription(Base):
#     __tablename__ = "prescriptions"
#     id = Column(Integer, primary_key=True, index=True)
#     patient_id = Column(Integer, ForeignKey("patients.id"))
#     doctor_id = Column(Integer, ForeignKey("doctors.id"))
#     drug_id = Column(Integer, ForeignKey("drugs.id"))
#     dosage = Column(String)
#     frequency = Column(String)
#     start_date = Column(Date)
#     end_date = Column(Date)
#     # ... other prescription details

# class Ward(Base):
#     __tablename__ = "wards"
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, unique=True)
#     capacity = Column(Integer)
#     # ...

# class Bed(Base):
#     __tablename__ = "beds"
#     id = Column(Integer, primary_key=True, index=True)
#     ward_id = Column(Integer, ForeignKey("wards.id"))
#     bed_number = Column(String)
#     is_occupied = Column(Boolean, default=False)
#     patient_id = Column(Integer, ForeignKey("patients.id"), nullable=True)
#     # ...