# 🩺 MedConnectAI — Smart Healthcare Management System

## 📘 Overview
MedConnectAI is a smart healthcare management system that integrates **Machine Learning (ML)** and **Large Language Models (LLMs)** to optimize hospital workflows.  
It predicts doctor availability, patient wait times, and enables an AI-driven chatbot for patient assistance.

---

## 🚀 Features
- 🧠 Predict hospital wait times using ML models
- 👨‍⚕️ Suggest best available doctors for specific symptoms
- 💬 AI Chatbot (powered by Hugging Face LLM)
- 📱 Notify patients via email/SMS simulation
- 🧾 Easy appointment booking and tracking system
- 🔍 API-based backend for integration with frontend or mobile apps

---

## 🏗️ Folder Structure

MedConnectAI/
├── backend/
│ ├── app.py
│ ├── db.py
│ ├── models.py
│ ├── routes/
│ ├── ml_models/
│ ├── utils/
│ ├── static/
│ └── templates/
├── frontend/
├── database/
├── run.py
├── requirements.txt
└── README.md



---

## ⚙️ Installation & Setup

1️⃣ **Clone the repository**
```bash
git clone https://github.com/yourusername/MedConnectAI.git
cd MedConnectAI


Create a virtual environment

python -m venv venv
# macOS/Linux
source venv/bin/activate
# Windows
venv\Scripts\activate


3️⃣ Install dependencies

pip install -r requirements.txt


4️⃣ Initialize the Database

from backend.db import db
from backend.app import create_app

app = create_app()
with app.app_context():
    db.create_all()


5️⃣ Run the Server

python run.py


The server will start on:
🔗 http://127.0.0.1:5000

🧠 ML Models

wait_time_model.pkl — predicts average patient wait times

doctor_suggestion.pkl — recommends doctors based on symptoms

Trained using Scikit-learn, integrated via Flask API

🤖 LLM Integration

Integrated with Hugging Face Transformers

Default model: distilgpt2 (can be replaced with healthcare-specific models later)

Provides AI-driven chatbot responses for patient queries

🧩 API Endpoints Summary
Endpoint	Method	Description
/api/patient/register	POST	Register new patient
/api/patient/book	POST	Book appointment
/api/doctor/login	POST	Doctor login
/api/doctor/logout	POST	Doctor logout
/api/notify/send	POST	Send notification to patient
/api/ml/waittime	POST	Predict patient wait time
/api/ml/doctor_suggestion	POST	Suggest alternate doctor
/api/chat	POST	AI Chatbot response
👥 Team Members
Name	Role
Gurupriya Avadhani M M	 Backend Developer
Hamsa Shree D N  	     AI/ML Developer
Praneetha	             Frontend Developer
🧾 License

MIT License © 2025 MedConnectAI Team