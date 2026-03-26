# doctor_routes.py (final)
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from backend.models import Doctor, Appointment, Notification
from backend.db import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

doctor_bp = Blueprint("doctor_bp", __name__)

@doctor_bp.route("/register", methods=["GET","POST"])
def doctor_register():
    if request.method == "POST":
        name = request.form.get("name")
        specialization = request.form.get("specialization")
        email = request.form.get("email")
        password = request.form.get("password")
        contact = request.form.get("contact","")
        hospital_id = request.form.get("hospital_id")
        existing = Doctor.query.filter_by(email=email).first()
        if existing:
            return render_template("doctor_register.html", error="Doctor already registered")
        new_doctor = Doctor(
            name=name,
            specialization=specialization,
            email=email,
            password=generate_password_hash(password),
            contact=contact,
            available=False,
            hospital_id=int(hospital_id) if hospital_id else None
        )
        db.session.add(new_doctor)
        db.session.commit()
        session["doctor_id"] = new_doctor.doctor_id
        session["user_type"] = "doctor"
        session["username"] = new_doctor.name
        return redirect(url_for("doctor_bp.doctor_dashboard"))
    return render_template("doctor_register.html")

@doctor_bp.route("/login", methods=["GET","POST"])
def doctor_login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        doctor = Doctor.query.filter_by(email=email).first()
        if doctor and check_password_hash(doctor.password, password):
            session["doctor_id"] = doctor.doctor_id
            session["user_type"] = "doctor"
            session["username"] = doctor.name
            return redirect(url_for("doctor_bp.doctor_dashboard"))
        return render_template("doctor_login.html", error="Invalid credentials")
    return render_template("doctor_login.html")

@doctor_bp.route("/dashboard")
def doctor_dashboard():
    doctor_id = session.get("doctor_id")
    if not doctor_id:
        return redirect(url_for("doctor_bp.doctor_login"))
    doctor = Doctor.query.get(doctor_id)
    appointments = Appointment.query.filter_by(doctor_id=doctor_id).all()
    return render_template("doctor_dashboard.html", doctor=doctor, appointments=appointments)

@doctor_bp.route("/update_availability", methods=["POST"])
def update_availability():
    data = request.get_json()
    doctor_id = session.get("doctor_id")
    available = data.get("available")
    if doctor_id is None or available is None:
        return jsonify({"error":"Available status required"}),400
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return jsonify({"error":"Doctor not found"}),404
    doctor.available = bool(available)
    db.session.commit()

    # If doctor went offline, notify patients who have upcoming appointments for that doctor
    try:
        if not doctor.available:
            upcoming = Appointment.query.filter(
                Appointment.doctor_id == doctor_id,
                Appointment.status.in_(["Booked", "Scheduled"])
            ).all()
            for appt in upcoming:
                try:
                    note = Notification(
                        patient_id=appt.patient_id,
                        message=f"Notice: Dr. {doctor.name} (hospital id {doctor.hospital_id or '—'}) has gone offline. Please check your appointment status.",
                        sent_time=datetime.now()
                    )
                    db.session.add(note)
                except Exception:
                    db.session.rollback()
            db.session.commit()
    except Exception:
        db.session.rollback()

    return jsonify({"message":"Availability updated successfully"}),200

@doctor_bp.route("/appointment/<int:appointment_id>/update_status", methods=["POST"])
def update_appointment_status(appointment_id):
    """Doctor updates an appointment status (Accepted / Rejected / Completed).
    Body: { "status": "Accepted" } etc.
    Notifies the patient when status changes.
    """
    doctor_id = session.get("doctor_id")
    if not doctor_id:
        return jsonify({"error":"Not logged in"}),403
    data = request.get_json() or {}
    new_status = data.get("status")
    if not new_status:
        return jsonify({"error":"status required"}),400

    appt = Appointment.query.get(appointment_id)
    if not appt:
        return jsonify({"error":"Appointment not found"}),404
    if appt.doctor_id != doctor_id:
        return jsonify({"error":"You are not authorized to modify this appointment"}),403

    old_status = appt.status
    appt.status = new_status
    db.session.commit()

    # Notify patient about the status update
    try:
        note = Notification(
            patient_id=appt.patient_id,
            message=f"Your appointment (id {appt.appointment_id}) with Dr. {Doctor.query.get(doctor_id).name} has been updated: {old_status} -> {new_status}.",
            sent_time=datetime.now()
        )
        db.session.add(note)
        db.session.commit()
    except Exception:
        db.session.rollback()

    return jsonify({"message":"Appointment status updated"}),200

@doctor_bp.route("/logout")
def doctor_logout():
    session.clear()
    return redirect(url_for("doctor_bp.doctor_login"))

@doctor_bp.route("/delete_account", methods=["POST"])
def delete_account():
    doctor_id = session.get("doctor_id")
    if not doctor_id:
        return jsonify({"error":"Not logged in"}),403
    doctor = Doctor.query.get(doctor_id)
    if doctor:
        Appointment.query.filter_by(doctor_id=doctor_id).delete()
        # Note: notifications table only references patients, so we do not delete doctor-specific notifications
        db.session.delete(doctor)
        db.session.commit()
    session.clear()
    return jsonify({"message":"Account deleted successfully"}),200


# from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
# from backend.models import Doctor, Appointment, Notification
# from backend.db import db
# from werkzeug.security import generate_password_hash, check_password_hash
# from datetime import datetime
# import hashlib

# doctor_bp = Blueprint("doctor_bp", __name__)

# def hash_hospital_id(hospital_id):
#     """Hash the hospital_id for privacy (still consistent for same id)."""
#     return hashlib.sha256(str(hospital_id).encode()).hexdigest()

# @doctor_bp.route("/register", methods=["GET", "POST"])
# def doctor_register():
#     if request.method == "POST":
#         name = request.form.get("name")
#         specialization = request.form.get("specialization")
#         email = request.form.get("email")
#         password = request.form.get("password")
#         contact = request.form.get("contact", "")
#         hospital_id = request.form.get("hospital_id")

#         existing = Doctor.query.filter_by(email=email).first()
#         if existing:
#             return render_template("doctor_register.html", error="Doctor already registered")

#         hashed_hosp_id = hash_hospital_id(hospital_id) if hospital_id else None

#         new_doctor = Doctor(
#             name=name,
#             specialization=specialization,
#             email=email,
#             password=generate_password_hash(password),
#             contact=contact,
#             available=False,
#             hospital_id_hashed=hashed_hosp_id
#         )

#         db.session.add(new_doctor)
#         db.session.commit()

#         session["doctor_id"] = new_doctor.doctor_id
#         session["user_type"] = "doctor"
#         session["username"] = new_doctor.name
#         return redirect(url_for("doctor_bp.doctor_dashboard"))

#     return render_template("doctor_register.html")


# @doctor_bp.route("/login", methods=["GET", "POST"])
# def doctor_login():
#     if request.method == "POST":
#         email = request.form.get("email")
#         password = request.form.get("password")
#         doctor = Doctor.query.filter_by(email=email).first()
#         if doctor and check_password_hash(doctor.password, password):
#             session["doctor_id"] = doctor.doctor_id
#             session["user_type"] = "doctor"
#             session["username"] = doctor.name
#             return redirect(url_for("doctor_bp.doctor_dashboard"))
#         return render_template("doctor_login.html", error="Invalid credentials")
#     return render_template("doctor_login.html")


# @doctor_bp.route("/dashboard")
# def doctor_dashboard():
#     doctor_id = session.get("doctor_id")
#     if not doctor_id:
#         return redirect(url_for("doctor_bp.doctor_login"))
#     doctor = Doctor.query.get(doctor_id)
#     appointments = Appointment.query.filter_by(doctor_id=doctor_id).all()
#     return render_template("doctor_dashboard.html", doctor=doctor, appointments=appointments)


# @doctor_bp.route("/update_availability", methods=["POST"])
# def update_availability():
#     data = request.get_json()
#     doctor_id = session.get("doctor_id")
#     available = data.get("available")

#     if doctor_id is None or available is None:
#         return jsonify({"error": "Available status required"}), 400

#     doctor = Doctor.query.get(doctor_id)
#     if not doctor:
#         return jsonify({"error": "Doctor not found"}), 404

#     doctor.available = bool(available)
#     db.session.commit()

#     try:
#         if not doctor.available:
#             upcoming = Appointment.query.filter(
#                 Appointment.doctor_id == doctor_id,
#                 Appointment.status.in_(["Booked", "Scheduled"])
#             ).all()
#             for appt in upcoming:
#                 note = Notification(
#                     patient_id=appt.patient_id,
#                     message=f"Notice: Dr. {doctor.name} has gone offline. Please check your appointment status.",
#                     sent_time=datetime.now()
#                 )
#                 db.session.add(note)
#             db.session.commit()
#     except Exception:
#         db.session.rollback()

#     return jsonify({"message": "Availability updated successfully"}), 200


# @doctor_bp.route("/appointment/<int:appointment_id>/update_status", methods=["POST"])
# def update_appointment_status(appointment_id):
#     doctor_id = session.get("doctor_id")
#     if not doctor_id:
#         return jsonify({"error": "Not logged in"}), 403

#     data = request.get_json() or {}
#     new_status = data.get("status")
#     if not new_status:
#         return jsonify({"error": "status required"}), 400

#     appt = Appointment.query.get(appointment_id)
#     if not appt:
#         return jsonify({"error": "Appointment not found"}), 404
#     if appt.doctor_id != doctor_id:
#         return jsonify({"error": "Unauthorized"}), 403

#     old_status = appt.status
#     appt.status = new_status
#     db.session.commit()

#     try:
#         note = Notification(
#             patient_id=appt.patient_id,
#             message=f"Your appointment (ID {appt.appointment_id}) with Dr. {Doctor.query.get(doctor_id).name} has been updated: {old_status} -> {new_status}.",
#             sent_time=datetime.now()
#         )
#         db.session.add(note)
#         db.session.commit()
#     except Exception:
#         db.session.rollback()

#     return jsonify({"message": "Appointment status updated"}), 200


# @doctor_bp.route("/logout")
# def doctor_logout():
#     session.clear()
#     return redirect(url_for("doctor_bp.doctor_login"))


# @doctor_bp.route("/delete_account", methods=["POST"])
# def delete_account():
#     doctor_id = session.get("doctor_id")
#     if not doctor_id:
#         return jsonify({"error": "Not logged in"}), 403
#     doctor = Doctor.query.get(doctor_id)
#     if doctor:
#         Appointment.query.filter_by(doctor_id=doctor_id).delete()
#         db.session.delete(doctor)
#         db.session.commit()
#     session.clear()
#     return jsonify({"message": "Account deleted successfully"}), 200
