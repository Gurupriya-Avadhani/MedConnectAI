import os
import random
from backend.app import create_app
from backend.db import db
from backend.models import Hospital, Doctor

# Delete old DB if exists
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../database/medconnectai.db"))
if os.path.exists(db_path):
    os.remove(db_path)
    print("🗑️ Old database deleted.")

# Initialize Flask app + db
app = create_app()
with app.app_context():
    db.create_all()
    print("✅ Tables created successfully!")

    # Add Hospitals
    if not Hospital.query.first():
        hospitals = [
            {"name": "Manipal Hospital", "latitude": 12.9716, "longitude": 77.5946},
            {"name": "Fortis Hospital", "latitude": 12.9352, "longitude": 77.6245},
            {"name": "Apollo Hospital", "latitude": 12.9279, "longitude": 77.6271},
            {"name": "Narayana Health", "latitude": 12.9822, "longitude": 77.5801},
            {"name": "Columbia Asia", "latitude": 12.9980, "longitude": 77.5670},
        ]
        objs = [Hospital(**h) for h in hospitals]
        db.session.add_all(objs)
        db.session.commit()
        print(f"🏥 Added {len(objs)} hospitals.")
    else:
        print("⚠️ Hospitals already exist.")

    # Add Doctors
    if not Doctor.query.first():
        names = [
            "Dr. Alice Smith", "Dr. Bob Johnson", "Dr. Carol Williams",
            "Dr. David Brown", "Dr. Emma Jones", "Dr. Frank Miller",
            "Dr. Grace Davis", "Dr. Henry Wilson"
        ]
        specs = ["Cardiology", "Neurology", "Pediatrics", "Orthopedics", "Dermatology", "Gynecology"]

        hospitals = Hospital.query.all()
        doctors = []
        for n in names:
            hosp = random.choice(hospitals)
            d = Doctor(
                name=n,
                specialization=random.choice(specs),
                experience=random.randint(3, 15),
                contact=f"+91-9{random.randint(100000000,999999999)}",
                available=True,
                hospital_id=hosp.hospital_id,
                latitude=hosp.latitude + random.uniform(-0.01, 0.01),
                longitude=hosp.longitude + random.uniform(-0.01, 0.01)
            )
            doctors.append(d)
        db.session.add_all(doctors)
        db.session.commit()
        print(f"👨‍⚕️ Added {len(doctors)} doctors.")
    else:
        print("⚠️ Doctors already exist.")

    print("🔍 Done!")
    print("Hospitals:", Hospital.query.count())
    print("Doctors:", Doctor.query.count())
