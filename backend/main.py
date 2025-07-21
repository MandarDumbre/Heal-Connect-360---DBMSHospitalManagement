# hms_backend/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm # For handling form data for login
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import date, datetime, timedelta

from . import crud, models, schemas, auth # Import auth module
from .database import SessionLocal, engine
from .chatbot_service import get_patient_info_from_chatbot

# Create database tables upon application startup (for development simplicity)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Hospital Management System API",
    description="A scalable API for managing hospital operations with AI Chatbot and JWT Authentication.",
    version="0.1.0"
)

# Configure CORS middleware
origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Authentication Endpoints ---

@app.post("/token", response_model=schemas.Token, tags=["Authentication"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticates a user and returns an access token.
    Requires username and password.
    """
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username, "roles": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED, tags=["Authentication"])
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new user.
    Only an Admin can register new users.
    """
    # This endpoint should ideally be protected so only an Admin can create new users.
    # For initial setup, we might allow it open, but for production, a specific admin token
    # should be required here.
    # For now, let's assume it's publicly accessible for easy testing, but note for future.

    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Hash the password before storing
    hashed_password = auth.get_password_hash(user.password)
    user_data = user.dict()
    user_data["hashed_password"] = hashed_password
    del user_data["password"] # Remove plain password

    return crud.create_user(db=db, user=schemas.UserCreateInDB(**user_data))

@app.get("/users/me/", response_model=schemas.User, tags=["Authentication"])
async def read_users_me(current_user: schemas.User = Depends(auth.get_current_active_user)):
    """
    Retrieves the current authenticated user's details.
    """
    return current_user

@app.get("/", tags=["Root"])
async def read_root():
    """
    Root endpoint for the API.
    """
    return {"message": "Welcome to the Hospital Management System API!"}

# --- Patient Endpoints (Protected) ---
@app.post("/patients/", response_model=schemas.Patient, status_code=status.HTTP_201_CREATED, tags=["Patients"])
def create_patient(patient: schemas.PatientCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    """
    Creates a new patient record. Requires authentication.
    Only Admin, Receptionist, or Nurse can create patients.
    """
    if current_user.role not in ["admin", "receptionist", "nurse"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create patients")
    db_patient = crud.get_patient_by_email(db, email=patient.email)
    if db_patient:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_patient(db=db, patient=patient)

@app.get("/patients/", response_model=List[schemas.Patient], tags=["Patients"])
def read_patients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    """
    Retrieves a list of all patients. Requires authentication.
    Accessible by Admin, Doctor, Receptionist, Nurse.
    """
    if current_user.role not in ["admin", "doctor", "receptionist", "nurse"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view all patients")
    patients = crud.get_patients(db, skip=skip, limit=limit)
    return patients

@app.get("/patients/{patient_id}", response_model=schemas.Patient, tags=["Patients"])
def read_patient(patient_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    """
    Retrieves a single patient by ID. Requires authentication.
    Accessible by Admin, Doctor (if assigned), Receptionist, Nurse.
    (Detailed doctor assignment check would be more complex here)
    """
    if current_user.role not in ["admin", "doctor", "receptionist", "nurse"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this patient")
    
    db_patient = crud.get_patient(db, patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Example of doctor-specific authorization (more complex in real app)
    # if current_user.role == "doctor" and not crud.is_doctor_assigned_to_patient(db, current_user.id, patient_id):
    #    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this patient's records")

    return db_patient

@app.put("/patients/{patient_id}", response_model=schemas.Patient, tags=["Patients"])
def update_patient(patient_id: int, patient: schemas.PatientUpdate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    """
    Updates an existing patient record. Requires authentication.
    Only Admin, Receptionist, or Nurse can update patients.
    """
    if current_user.role not in ["admin", "receptionist", "nurse"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update patients")
    db_patient = crud.update_patient(db, patient_id=patient_id, patient_data=patient)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return db_patient

@app.delete("/patients/{patient_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Patients"])
def delete_patient(patient_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    """
    Deletes a patient record. Requires authentication.
    Only Admin can delete patients.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete patients")
    success = crud.delete_patient(db, patient_id=patient_id)
    if not success:
        raise HTTPException(status_code=404, detail="Patient not found")
    return

# --- Doctor Endpoints (Protected) ---
@app.post("/doctors/", response_model=schemas.Doctor, status_code=status.HTTP_201_CREATED, tags=["Doctors"])
def create_doctor(doctor: schemas.DoctorCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    """
    Creates a new doctor record. Requires authentication.
    Only Admin can create doctors.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create doctors")
    db_doctor = crud.get_doctor_by_email(db, email=doctor.email)
    if db_doctor:
        raise HTTPException(status_code=400, detail="Doctor with this email already registered")
    return crud.create_doctor(db=db, doctor=doctor)

@app.get("/doctors/", response_model=List[schemas.Doctor], tags=["Doctors"])
def read_doctors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    """
    Retrieves a list of all doctors. Requires authentication.
    Accessible by Admin, Doctor, Receptionist, Nurse.
    """
    if current_user.role not in ["admin", "doctor", "receptionist", "nurse"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view doctors")
    doctors = crud.get_doctors(db, skip=skip, limit=limit)
    return doctors

@app.get("/doctors/{doctor_id}", response_model=schemas.Doctor, tags=["Doctors"])
def read_doctor(doctor_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    """
    Retrieves a single doctor by ID. Requires authentication.
    Accessible by Admin, Doctor, Receptionist, Nurse.
    """
    if current_user.role not in ["admin", "doctor", "receptionist", "nurse"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this doctor")
    db_doctor = crud.get_doctor(db, doctor_id=doctor_id)
    if db_doctor is None:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return db_doctor

@app.put("/doctors/{doctor_id}", response_model=schemas.Doctor, tags=["Doctors"])
def update_doctor(doctor_id: int, doctor: schemas.DoctorUpdate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    """
    Updates an existing doctor record. Requires authentication.
    Only Admin can update doctors.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update doctors")
    db_doctor = crud.update_doctor(db, doctor_id=doctor_id, doctor_data=doctor)
    if db_doctor is None:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return db_doctor

@app.delete("/doctors/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Doctors"])
def delete_doctor(doctor_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    """
    Deletes a doctor record. Requires authentication.
    Only Admin can delete doctors.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete doctors")
    success = crud.delete_doctor(db, doctor_id=doctor_id)
    if not success:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return

# --- Appointment Endpoints (Protected) ---
@app.post("/appointments/", response_model=schemas.Appointment, status_code=status.HTTP_201_CREATED, tags=["Appointments"])
def create_appointment(appointment: schemas.AppointmentCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    """
    Creates a new appointment. Requires authentication.
    Only Admin, Receptionist, or Nurse can create appointments.
    """
    if current_user.role not in ["admin", "receptionist", "nurse"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create appointments")

    patient = crud.get_patient(db, appointment.patient_id)
    doctor = crud.get_doctor(db, appointment.doctor_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    return crud.create_appointment(db=db, appointment=appointment)

@app.get("/appointments/", response_model=List[schemas.Appointment], tags=["Appointments"])
def read_appointments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    """
    Retrieves a list of all appointments. Requires authentication.
    Accessible by Admin, Doctor, Receptionist, Nurse.
    """
    if current_user.role not in ["admin", "doctor", "receptionist", "nurse"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view all appointments")
    appointments = db.query(models.Appointment).options(
        joinedload(models.Appointment.patient),
        joinedload(models.Appointment.doctor)
    ).offset(skip).limit(limit).all()
    return appointments

@app.get("/appointments/patient/{patient_id}", response_model=List[schemas.Appointment], tags=["Appointments"])
def read_patient_appointments(patient_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    """
    Retrieves all appointments for a specific patient. Requires authentication.
    Accessible by Admin, Doctor (if assigned), Receptionist, Nurse.
    """
    if current_user.role not in ["admin", "doctor", "receptionist", "nurse"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this patient's appointments")
    
    patient = crud.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Example of doctor-specific authorization for appointments
    # if current_user.role == "doctor" and not crud.is_doctor_assigned_to_patient_appointments(db, current_user.id, patient_id):
    #    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this patient's appointments")

    appointments = db.query(models.Appointment).filter(models.Appointment.patient_id == patient_id).options(
        joinedload(models.Appointment.patient),
        joinedload(models.Appointment.doctor)
    ).all()
    return appointments

@app.put("/appointments/{appointment_id}", response_model=schemas.Appointment, tags=["Appointments"])
def update_appointment(appointment_id: int, appointment_data: schemas.AppointmentUpdate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    """
    Updates an existing appointment record. Requires authentication.
    Only Admin, Receptionist, or Nurse can update appointments.
    """
    if current_user.role not in ["admin", "receptionist", "nurse"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update appointments")
    db_appointment = crud.update_appointment(db, appointment_id=appointment_id, appointment_data=appointment_data)
    if db_appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return db_appointment

@app.delete("/appointments/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Appointments"])
def delete_appointment(appointment_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    """
    Deletes an appointment record. Requires authentication.
    Only Admin can delete appointments.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete appointments")
    success = crud.delete_appointment(db, appointment_id=appointment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return

# --- Patient Visit (EHR/EMR - Single Appointment Form) Endpoints (Protected) ---
@app.post("/patient_visits/", response_model=schemas.PatientVisit, status_code=status.HTTP_201_CREATED, tags=["Patient Visits"])
def create_patient_visit(visit: schemas.PatientVisitCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    """
    Creates a new patient visit record (EHR/EMR entry). Requires authentication.
    Only Doctor or Nurse can create visit records.
    """
    if current_user.role not in ["doctor", "nurse"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create patient visit records")

    patient = crud.get_patient(db, visit.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    if visit.doctor_id:
        doctor = crud.get_doctor(db, visit.doctor_id)
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")
    return crud.create_patient_visit(db=db, visit=visit)

@app.get("/patient_visits/patient/{patient_id}", response_model=List[schemas.PatientVisit], tags=["Patient Visits"])
def get_patient_visit_history(patient_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    """
    Retrieves all visit records for a specific patient. Requires authentication.
    Accessible by Admin, Doctor (if assigned), Nurse.
    """
    if current_user.role not in ["admin", "doctor", "nurse"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view patient visit history")
    
    patient = crud.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Example of doctor-specific authorization for visit history
    # if current_user.role == "doctor" and not crud.is_doctor_assigned_to_patient_visits(db, current_user.id, patient_id):
    #    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this patient's visit history")

    visits = db.query(models.PatientVisit).filter(models.PatientVisit.patient_id == patient_id).options(
        joinedload(models.PatientVisit.patient),
        joinedload(models.PatientVisit.doctor)
    ).all()
    return visits

@app.get("/patient_visits/{visit_id}", response_model=schemas.PatientVisit, tags=["Patient Visits"])
def get_patient_visit(visit_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    """
    Retrieves a single patient visit record by ID. Requires authentication.
    Accessible by Admin, Doctor (if assigned), Nurse.
    """
    if current_user.role not in ["admin", "doctor", "nurse"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this patient visit record")
    
    db_visit = db.query(models.PatientVisit).filter(models.PatientVisit.id == visit_id).options(
        joinedload(models.PatientVisit.patient),
        joinedload(models.PatientVisit.doctor)
    ).first()
    if db_visit is None:
        raise HTTPException(status_code=404, detail="Patient visit record not found")
    
    # Example of doctor-specific authorization for a single visit
    # if current_user.role == "doctor" and db_visit.doctor_id != current_user.id:
    #    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this specific visit record")

    return db_visit

@app.put("/patient_visits/{visit_id}", response_model=schemas.PatientVisit, tags=["Patient Visits"])
def update_patient_visit(visit_id: int, visit_data: schemas.PatientVisitUpdate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    """
    Updates an existing patient visit record. Requires authentication.
    Only Doctor or Nurse can update visit records.
    """
    if current_user.role not in ["doctor", "nurse"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update patient visit records")
    db_visit = crud.update_patient_visit(db, visit_id=visit_id, visit_data=visit_data)
    if db_visit is None:
        raise HTTPException(status_code=404, detail="Patient visit record not found")
    return db_visit

@app.delete("/patient_visits/{visit_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Patient Visits"])
def delete_patient_visit(visit_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    """
    Deletes a patient visit record. Requires authentication.
    Only Admin can delete visit records.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete patient visit records")
    success = crud.delete_patient_visit(db, visit_id=visit_id)
    if not success:
        raise HTTPException(status_code=404, detail="Patient visit record not found")
    return

# --- AI Chatbot Endpoint (Protected) ---
@app.post("/chatbot/query", response_model=schemas.ChatbotResponse, tags=["AI Chatbot"])
def chatbot_query(query_request: schemas.ChatbotQuery, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_active_user)):
    """
    Endpoint for the AI chatbot to query patient information. Requires authentication.
    Accessible by Admin and Doctor roles.
    """
    if current_user.role not in ["admin", "doctor"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to use the chatbot for patient information.")

    response_text = get_patient_info_from_chatbot(
        query=query_request.query,
        db=db,
        user_role=current_user.role, # Pass role from authenticated user
        user_id=current_user.id # Pass ID from authenticated user
    )
    return schemas.ChatbotResponse(response=response_text)
