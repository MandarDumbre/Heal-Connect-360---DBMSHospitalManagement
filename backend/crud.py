# hms_backend/crud.py
from sqlalchemy.orm import Session
from sqlalchemy import or_
from . import models, schemas
from typing import List, Optional
from datetime import datetime, date

# --- User CRUD Operations ---
def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreateInDB) -> models.User:
    db_user = models.User(username=user.username, hashed_password=user.hashed_password, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- Patient CRUD Operations ---
def get_patient(db: Session, patient_id: int) -> Optional[models.Patient]:
    return db.query(models.Patient).filter(models.Patient.id == patient_id).first()

def get_patient_by_email(db: Session, email: str) -> Optional[models.Patient]:
    return db.query(models.Patient).filter(models.Patient.email == email).first()

def get_patients(db: Session, skip: int = 0, limit: int = 100) -> List[models.Patient]:
    return db.query(models.Patient).offset(skip).limit(limit).all()

def create_patient(db: Session, patient: schemas.PatientCreate) -> models.Patient:
    db_patient = models.Patient(**patient.dict())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

def update_patient(db: Session, patient_id: int, patient_data: schemas.PatientUpdate) -> Optional[models.Patient]:
    db_patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if db_patient:
        for key, value in patient_data.dict(exclude_unset=True).items():
            setattr(db_patient, key, value)
        db.add(db_patient)
        db.commit()
        db.refresh(db_patient)
    return db_patient

def delete_patient(db: Session, patient_id: int) -> bool:
    db_patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if db_patient:
        db.delete(db_patient)
        db.commit()
        return True
    return False

# --- Doctor CRUD Operations ---
def get_doctor(db: Session, doctor_id: int) -> Optional[models.Doctor]:
    return db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()

def get_doctor_by_email(db: Session, email: str) -> Optional[models.Doctor]:
    return db.query(models.Doctor).filter(models.Doctor.email == email).first()

def get_doctors(db: Session, skip: int = 0, limit: int = 100) -> List[models.Doctor]:
    return db.query(models.Doctor).offset(skip).limit(limit).all()

def create_doctor(db: Session, doctor: schemas.DoctorCreate) -> models.Doctor:
    db_doctor = models.Doctor(**doctor.dict())
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    return db_doctor

def update_doctor(db: Session, doctor_id: int, doctor_data: schemas.DoctorUpdate) -> Optional[models.Doctor]:
    db_doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if db_doctor:
        for key, value in doctor_data.dict(exclude_unset=True).items():
            setattr(db_doctor, key, value)
        db.add(db_doctor)
        db.commit()
        db.refresh(db_doctor)
    return db_doctor

def delete_doctor(db: Session, doctor_id: int) -> bool:
    db_doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if db_doctor:
        db.delete(db_doctor)
        db.commit()
        return True
    return False

# --- Appointment CRUD Operations ---
def get_appointment(db: Session, appointment_id: int) -> Optional[models.Appointment]:
    return db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()

def get_appointments_by_patient(db: Session, patient_id: int) -> List[models.Appointment]:
    return db.query(models.Appointment).filter(models.Appointment.patient_id == patient_id).all()

def get_appointments_by_doctor(db: Session, doctor_id: int) -> List[models.Appointment]:
    return db.query(models.Appointment).filter(models.Appointment.doctor_id == doctor_id).all()

def create_appointment(db: Session, appointment: schemas.AppointmentCreate) -> models.Appointment:
    db_appointment = models.Appointment(**appointment.dict())
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

def update_appointment(db: Session, appointment_id: int, appointment_data: schemas.AppointmentUpdate) -> Optional[models.Appointment]:
    db_appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if db_appointment:
        for key, value in appointment_data.dict(exclude_unset=True).items():
            setattr(db_appointment, key, value)
        db.add(db_appointment)
        db.commit()
        db.refresh(db_appointment)
    return db_appointment

def delete_appointment(db: Session, appointment_id: int) -> bool:
    db_appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()
    if db_appointment:
        db.delete(db_appointment)
        db.commit()
        return True
    return False

# --- Patient Visit (EHR/EMR) CRUD Operations ---
def get_patient_visit(db: Session, visit_id: int) -> Optional[models.PatientVisit]:
    return db.query(models.PatientVisit).filter(models.PatientVisit.id == visit_id).first()

def get_patient_visits_by_patient(db: Session, patient_id: int) -> List[models.PatientVisit]:
    return db.query(models.PatientVisit).filter(models.PatientVisit.patient_id == patient_id).all()

def create_patient_visit(db: Session, visit: schemas.PatientVisitCreate) -> models.PatientVisit:
    db_visit = models.PatientVisit(**visit.dict())
    db.add(db_visit)
    db.commit()
    db.refresh(db_visit)
    return db_visit

def update_patient_visit(db: Session, visit_id: int, visit_data: schemas.PatientVisitUpdate) -> Optional[models.PatientVisit]:
    db_visit = db.query(models.PatientVisit).filter(models.PatientVisit.id == visit_id).first()
    if db_visit:
        for key, value in visit_data.dict(exclude_unset=True).items():
            setattr(db_visit, key, value)
        db.add(db_visit)
        db.commit()
        db.refresh(db_visit)
    return db_visit

def delete_patient_visit(db: Session, visit_id: int) -> bool:
    db_visit = db.query(models.PatientVisit).filter(models.PatientVisit.id == visit_id).first()
    if db_visit:
        db.delete(db_visit)
        db.commit()
        return True
    return False
