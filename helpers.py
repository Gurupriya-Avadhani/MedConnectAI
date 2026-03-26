# def format_doctor_data(doctor):
#     return {
#         "doctor_id": doctor.doctor_id,
#         "name": doctor.name,
#         "specialization": doctor.specialization,
#         "experience": doctor.experience,
#         "contact": doctor.contact,
#         "available": doctor.available
#     }



# helpers.py
import hashlib

def hash_hospital_id(hospital_id):
    """Return a deterministic SHA-256 hash for the hospital ID."""
    if hospital_id is None:
        return None
    raw = str(hospital_id).encode()
    return hashlib.sha256(raw).hexdigest()[:12]   # short 12-char hash

def format_doctor_data(doctor):
    return {
        "doctor_id": doctor.doctor_id,
        "name": doctor.name,
        "specialization": doctor.specialization,
        "experience": doctor.experience,
        "contact": doctor.contact,
        "available": doctor.available,
        "hospital_hashed_id": hash_hospital_id(doctor.hospital_id)
    }
