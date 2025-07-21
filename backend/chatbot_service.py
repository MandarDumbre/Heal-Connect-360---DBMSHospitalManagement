# hms_backend/chatbot_service.py
from sqlalchemy.orm import Session, joinedload
from . import crud, models
from typing import Optional, List
from datetime import datetime, date

# This function simulates the interaction with an LLM and your database.
# In a real-world scenario with a fully free and open-source stack, this would involve:
# 1. Sending the 'query' to a self-hosted LLM (e.g., Llama 3 running via Ollama/vLLM).
#    This would typically be an HTTP request to your local LLM inference server.
# 2. The LLM interpreting the natural language query to understand user intent
#    (e.g., "get patient details", "list all patients", "summarize medical history").
# 3. The LLM (or a "tool-calling" mechanism/RAG pipeline) generating appropriate
#    database queries or calling specific `crud` functions based on its understanding.
#    For example, if the query is "What are John Doe's vital signs?", the LLM would
#    identify "John Doe" and "vital signs" and then instruct the system to call a
#    `crud` function to fetch John Doe's vital signs from the database.
# 4. The LLM formatting the retrieved data into a coherent and natural language response.
#
# This mock implementation uses simple string matching and direct `crud` calls
# to simulate the data retrieval part.

def get_patient_info_from_chatbot(query: str, db: Session, user_role: str, user_id: int) -> str: # user_id is now int
    """
    Simulates an AI chatbot's response based on a natural language query and database interaction.
    Includes basic authorization logic.

    Args:
        query (str): The natural language query from the user.
        db (Session): The SQLAlchemy database session.
        user_role (str): The role of the authenticated user (e.g., "admin", "doctor").
        user_id (int): The ID of the authenticated user.

    Returns:
        str: The chatbot's natural language response.
    """
    # --- Authorization Check ---
    # The main.py already restricts access to this endpoint to "admin" and "doctor" roles.
    # Here, we can add more granular checks if needed (e.g., doctor can only query their patients).
    if user_role not in ["admin", "doctor"]:
        # This should ideally be caught by main.py's dependency, but as a safeguard.
        return "Access denied. You are not authorized to use the chatbot for patient information."

    query_lower = query.lower()
    response = "I'm sorry, I couldn't understand that query. Please try rephrasing or ask about patient ID, doctor ID, appointments, or patient visit history."

    # --- Simulate LLM understanding and data retrieval based on query ---

    # Example 1: Query for a specific patient's details by ID
    if "patient" in query_lower and ("id" in query_lower or "details" in query_lower):
        try:
            patient_id_str = ''.join(filter(str.isdigit, query_lower))
            if patient_id_str:
                patient_id = int(patient_id_str)
                patient = crud.get_patient(db, patient_id)
                if patient:
                    # More granular authorization: Doctors can only see their assigned patients
                    # (Requires a more complex patient-doctor assignment in the DB)
                    # For now, assuming doctors can see any patient for demo simplicity
                    response = (
                        f"Patient ID: {patient.id}\n"
                        f"Name: {patient.first_name} {patient.last_name}\n"
                        f"Email: {patient.email}\n"
                        f"Phone: {patient.phone_number}\n"
                        f"Date of Birth: {patient.date_of_birth}\n"
                        f"Address: {patient.address}\n"
                        f"Gender: {patient.gender}"
                    )
                else:
                    response = f"Patient with ID {patient_id} not found."
            else:
                response = "Please specify a patient ID (e.g., 'What are the details for patient ID 1?')."
        except ValueError:
            response = "Could not parse patient ID from your query. Please ensure it's a number."
        except Exception as e:
            response = f"An error occurred while fetching patient details: {e}"

    # Example 2: Query to list all patients (typically for admin)
    elif "all patients" in query_lower or "list patients" in query_lower:
        if user_role == "admin":
            patients = crud.get_patients(db, limit=10) # Limit for brevity
            if patients:
                patient_list = "\n".join([f"- {p.first_name} {p.last_name} (ID: {p.id}, Email: {p.email})" for p in patients])
                response = f"Here are some patients:\n{patient_list}"
            else:
                response = "No patients found in the system."
        else:
            response = "You are not authorized to list all patients."

    # Example 3: Query for a specific doctor's details by ID
    elif "doctor" in query_lower and ("id" in query_lower or "details" in query_lower):
        try:
            doctor_id_str = ''.join(filter(str.isdigit, query_lower))
            if doctor_id_str:
                doctor_id = int(doctor_id_str)
                doctor = crud.get_doctor(db, doctor_id)
                if doctor:
                    response = (
                        f"Doctor ID: {doctor.id}\n"
                        f"Name: {doctor.first_name} {doctor.last_name}\n"
                        f"Email: {doctor.email}\n"
                        f"Specialization: {doctor.specialization}\n"
                        f"Phone: {doctor.phone_number}\n"
                        f"License: {doctor.license_number}"
                    )
                else:
                    response = f"Doctor with ID {doctor_id} not found."
            else:
                response = "Please specify a doctor ID (e.g., 'What are the details for doctor ID 1?')."
        except ValueError:
            response = "Could not parse doctor ID from your query. Please ensure it's a number."
        except Exception as e:
            response = f"An error occurred while fetching doctor details: {e}"

    # Example 4: Query to list all doctors (typically for admin)
    elif "all doctors" in query_lower or "list doctors" in query_lower:
        if user_role == "admin":
            doctors = crud.get_doctors(db, limit=10)
            if doctors:
                doctor_list = "\n".join([f"- {d.first_name} {d.last_name} (ID: {d.id}, Spec: {d.specialization})" for d in doctors])
                response = f"Here are some doctors:\n{doctor_list}"
            else:
                response = "No doctors found in the system."
        else:
            response = "You are not authorized to list all doctors."

    # Example 5: Query for a patient's appointments
    elif "patient" in query_lower and "appointments" in query_lower:
        try:
            patient_id_str = ''.join(filter(str.isdigit, query_lower))
            if patient_id_str:
                patient_id = int(patient_id_str)
                patient = crud.get_patient(db, patient_id)
                if not patient:
                    response = f"Patient with ID {patient_id} not found."
                else:
                    # Fetch appointments and eager load patient/doctor details
                    appointments = db.query(models.Appointment).filter(models.Appointment.patient_id == patient_id).options(
                        joinedload(models.Appointment.patient),
                        joinedload(models.Appointment.doctor)
                    ).all()
                    if appointments:
                        app_list = []
                        for app in appointments:
                            doctor_name = f"{app.doctor.first_name} {app.doctor.last_name}" if app.doctor else 'N/A'
                            app_list.append(
                                f"- Appt ID: {app.id}, Doctor: {doctor_name}, "
                                f"Time: {app.appointment_time.strftime('%Y-%m-%d %H:%M')}, Reason: {app.reason}, Status: {app.status}"
                            )
                        response = f"Appointments for Patient {patient.first_name} {patient.last_name} (ID: {patient_id}):\n" + "\n".join(app_list)
                    else:
                        response = f"No appointments found for Patient ID {patient_id}."
            else:
                response = "Please specify a patient ID for appointments (e.g., 'Show appointments for patient ID 1')."
        except ValueError:
            response = "Could not parse patient ID from your query. Please ensure it's a number."
        except Exception as e:
            response = f"An error occurred while fetching appointments: {e}"

    # Example 6: Query for a patient's visit history (EHR/EMR)
    elif "patient" in query_lower and ("visit history" in query_lower or "medical records" in query_lower or "ehr" in query_lower):
        try:
            patient_id_str = ''.join(filter(str.isdigit, query_lower))
            if patient_id_str:
                patient_id = int(patient_id_str)
                patient = crud.get_patient(db, patient_id)
                if not patient:
                    response = f"Patient with ID {patient_id} not found."
                else:
                    # Fetch patient visits and eager load patient/doctor details
                    visits = db.query(models.PatientVisit).filter(models.PatientVisit.patient_id == patient_id).options(
                        joinedload(models.PatientVisit.patient),
                        joinedload(models.PatientVisit.doctor)
                    ).all()
                    if visits:
                        visit_summaries = []
                        for visit in visits:
                            doctor_name = f"{visit.doctor.first_name} {visit.doctor.last_name}" if visit.doctor else 'N/A'
                            visit_summaries.append(
                                f"- Visit ID: {visit.id}, Date: {visit.visit_date.strftime('%Y-%m-%d %H:%M')}, "
                                f"Doctor: {doctor_name}\n"
                                f"  Chief Complaint: {visit.chief_complaint or 'N/A'}\n"
                                f"  Diagnosis: {visit.diagnosis or 'N/A'}\n"
                                f"  Treatment: {visit.treatment or 'N/A'}"
                            )
                        response = f"Visit history for Patient {patient.first_name} {patient.last_name} (ID: {patient_id}):\n" + "\n\n".join(visit_summaries)
                    else:
                        response = f"No visit history found for Patient ID {patient_id}."
            else:
                response = "Please specify a patient ID for visit history (e.g., 'Show medical records for patient ID 1')."
        except ValueError:
            response = "Could not parse patient ID from your query. Please ensure it's a number."
        except Exception as e:
            response = f"An error occurred while fetching visit history: {e}"

    # Example 7: Simple greeting
    elif "hello" in query_lower or "hi" in query_lower:
        response = "Hello! How can I assist you with patient information today?"

    return response