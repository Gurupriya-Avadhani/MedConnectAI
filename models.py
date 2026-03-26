# from datetime import datetime
# from backend.db import db

# class Hospital(db.Model):
#     __tablename__ = "hospitals"
#     hospital_id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     address = db.Column(db.String(200), nullable=True)
#     latitude = db.Column(db.Float, nullable=True)
#     longitude = db.Column(db.Float, nullable=True)
#     doctors = db.relationship("Doctor", backref="hospital", lazy=True)

# class Doctor(db.Model):
#     __tablename__ = "doctors"
#     doctor_id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     password = db.Column(db.String(200), nullable=False)
#     specialization = db.Column(db.String(100), nullable=False)
#     experience = db.Column(db.Integer, nullable=True)
#     contact = db.Column(db.String(20), nullable=True)
#     available = db.Column(db.Boolean, default=True)
#     latitude = db.Column(db.Float, nullable=True)
#     longitude = db.Column(db.Float, nullable=True)
#     status = db.Column(db.String(50), default="Available")
#     hospital_id = db.Column(db.Integer, db.ForeignKey("hospitals.hospital_id"), nullable=True)
#     appointments = db.relationship("Appointment", backref="doctor", lazy=True)

# class Patient(db.Model):
#     __tablename__ = "patients"
#     patient_id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     password = db.Column(db.String(200), nullable=False)
#     age = db.Column(db.Integer, nullable=True)
#     gender = db.Column(db.String(10), nullable=True)
#     contact = db.Column(db.String(20), nullable=True)
#     latitude = db.Column(db.Float, nullable=True)
#     longitude = db.Column(db.Float, nullable=True)
#     appointments = db.relationship("Appointment", backref="patient", lazy=True)
#     notifications = db.relationship("Notification", backref="patient", lazy=True)

# class Appointment(db.Model):
#     __tablename__ = "appointments"
#     appointment_id = db.Column(db.Integer, primary_key=True)
#     doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.doctor_id"), nullable=False)
#     patient_id = db.Column(db.Integer, db.ForeignKey("patients.patient_id"), nullable=False)
#     appointment_date = db.Column(db.Date, nullable=False)
#     appointment_time = db.Column(db.Time, nullable=False)
#     start_time = db.Column(db.DateTime, nullable=True)
#     end_time = db.Column(db.DateTime, nullable=True)
#     wait_time = db.Column(db.Float, nullable=True)
#     status = db.Column(db.String(20), default="Booked")

# class Notification(db.Model):
#     __tablename__ = "notifications"
#     notification_id = db.Column(db.Integer, primary_key=True)
#     patient_id = db.Column(db.Integer, db.ForeignKey("patients.patient_id"), nullable=False)
#     message = db.Column(db.String(300), nullable=False)
#     sent_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)




from datetime import datetime
from backend.db import db
from backend.utils.helpers import hash_hospital_id


class Hospital(db.Model):
    __tablename__ = "hospitals"
    hospital_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    doctors = db.relationship("Doctor", backref="hospital", lazy=True)

    @property
    def hashed_id(self):
        return hash_hospital_id(self.hospital_id)


class Doctor(db.Model):
    __tablename__ = "doctors"
    doctor_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    experience = db.Column(db.Integer, nullable=True)
    contact = db.Column(db.String(20), nullable=True)
    available = db.Column(db.Boolean, default=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(50), default="Available")
    hospital_id = db.Column(db.Integer, db.ForeignKey("hospitals.hospital_id"), nullable=True)

    appointments = db.relationship("Appointment", backref="doctor", lazy=True)


class Patient(db.Model):
    __tablename__ = "patients"
    patient_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    contact = db.Column(db.String(20), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    appointments = db.relationship("Appointment", backref="patient", lazy=True)
    notifications = db.relationship("Notification", backref="patient", lazy=True)


class Appointment(db.Model):
    __tablename__ = "appointments"
    appointment_id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.doctor_id"), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.patient_id"), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.Time, nullable=False)
    start_time = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)
    wait_time = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), default="Booked")


class Notification(db.Model):
    __tablename__ = "notifications"
    notification_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.patient_id"), nullable=False)
    message = db.Column(db.String(300), nullable=False)
    sent_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
