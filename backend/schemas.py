# hms_backend/schemas.py
from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional, List, Literal

# --- User Schemas (for Authentication) ---
class UserBase(BaseModel):
    username: str
    # Define roles: admin, doctor, nurse, receptionist, patient, pharmacist
    role: Literal["admin", "doctor", "nurse", "receptionist", "patient", "pharmacist"]

class UserCreate(UserBase):
    password: str

class UserCreateInDB(UserBase):
    hashed_password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

# --- JWT Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    roles: Optional[str] = None # Store roles as a string (e.g., "admin,doctor") or single role

# --- Patient Schemas ---
class PatientBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    date_of_birth: date
    address: str
    gender: Literal['Male', 'Female', 'Other', 'Prefer not to say']

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    gender: Optional[Literal['Male', 'Female', 'Other', 'Prefer not to say']] = None

class Patient(PatientBase):
    id: int
    class Config:
        from_attributes = True

# --- Doctor Schemas ---
class DoctorBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    specialization: str
    license_number: str

class DoctorCreate(DoctorBase):
    pass

class DoctorUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    specialization: Optional[str] = None
    license_number: Optional[str] = None

class Doctor(DoctorBase):
    id: int
    class Config:
        from_attributes = True

# --- Appointment Schemas ---
class AppointmentBase(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_time: datetime
    reason: str
    status: Literal['Scheduled', 'Completed', 'Cancelled'] = 'Scheduled'

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentUpdate(BaseModel):
    patient_id: Optional[int] = None
    doctor_id: Optional[int] = None
    appointment_time: Optional[datetime] = None
    reason: Optional[str] = None
    status: Optional[Literal['Scheduled', 'Completed', 'Cancelled']] = None

class Appointment(AppointmentBase):
    id: int
    # Include related models for a richer response
    patient: Optional[Patient] = None
    doctor: Optional[Doctor] = None

    class Config:
        from_attributes = True

# --- Patient Visit (EHR/EMR) Schemas ---
class PatientVisitBase(BaseModel):
    patient_id: int
    doctor_id: Optional[int] = None
    visit_date: datetime = datetime.utcnow()

    chief_complaint: Optional[str] = None
    clinical_notes: Optional[str] = None

    blood_pressure: Optional[str] = None
    temperature: Optional[str] = None
    pulse_rate: Optional[int] = None
    respiration_rate: Optional[int] = None
    weight_kg: Optional[str] = None
    height_cm: Optional[str] = None

    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    procedures_performed: Optional[str] = None
    prescriptions: Optional[str] = None
    follow_up_instructions: Optional[str] = None
    next_appointment_date: Optional[date] = None

class PatientVisitCreate(PatientVisitBase):
    pass

class PatientVisitUpdate(BaseModel):
    patient_id: Optional[int] = None
    doctor_id: Optional[int] = None
    visit_date: Optional[datetime] = None

    chief_complaint: Optional[str] = None
    clinical_notes: Optional[str] = None

    blood_pressure: Optional[str] = None
    temperature: Optional[str] = None
    pulse_rate: Optional[int] = None
    respiration_rate: Optional[int] = None
    weight_kg: Optional[str] = None
    height_cm: Optional[str] = None

    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    procedures_performed: Optional[str] = None
    prescriptions: Optional[str] = None
    follow_up_instructions: Optional[str] = None
    next_appointment_date: Optional[date] = None

class PatientVisit(PatientVisitBase):
    id: int
    # Include related models for a richer response
    patient: Optional[Patient] = None
    doctor: Optional[Doctor] = None

    class Config:
        from_attributes = True

# --- Chatbot Schemas (Simplified for authenticated context) ---
class ChatbotQuery(BaseModel):
    query: str
    # user_role and user_id are now derived from the authenticated JWT token,
    # so they are removed from the request body.

class ChatbotResponse(BaseModel):
    response: str