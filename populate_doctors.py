from backend.app import create_app
from backend.db import db
from backend.models import Doctor, Hospital
import random

app = create_app()

with app.app_context():
    hospitals = Hospital.query.all()
    if not hospitals:
        print("⚠️ No hospitals found! Run init_db.py first to add hospitals.")
        exit()

    # Dummy doctor names and specializations
    doctor_names = [
        "Dr. Alice Smith", "Dr. Bob Johnson", "Dr. Carol Williams",
        "Dr. David Brown", "Dr. Emma Jones", "Dr. Frank Miller",
        "Dr. Grace Davis", "Dr. Henry Wilson"
    ]

    specializations = [
        "Cardiology", "Neurology", "Pediatrics", "Orthopedics",
        "Dermatology", "Gynecology", "General Medicine"
    ]

    # Avoid duplicating doctors
    if Doctor.query.first():
        print("⚠️ Doctors already exist in DB. Skipping population.")
        exit()

    doctors = []
    for i in range(len(doctor_names)):
        hospital = random.choice(hospitals)
        doctor = Doctor(
            name=doctor_names[i],
            specialization=random.choice(specializations),
            experience=random.randint(3, 15),
            contact=f"+91-9{random.randint(100000000,999999999)}",
            available=bool(random.getrandbits(1)),
            hospital_id=hospital.hospital_id
        )
        doctors.append(doctor)

    db.session.add_all(doctors)
    db.session.commit()
    print(f"✅ Added {len(doctors)} dummy doctors linked to real hospitals.")
