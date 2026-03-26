from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import sqlite3

tokenizer = AutoTokenizer.from_pretrained("bigscience/bloom-560m")
model = AutoModelForCausalLM.from_pretrained("bigscience/bloom-560m")

DB_PATH = "../database/medconnectai.db"

def query_doctor_info(question: str) -> str:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if "specialization" in question.lower():
        cursor.execute("SELECT name, specialization FROM Doctor")
        rows = cursor.fetchall()
        result = " | ".join([f"{name} ({spec})" for name, spec in rows])
    elif "appointment" in question.lower():
        cursor.execute("SELECT patient_id, doctor_id, appointment_date FROM Appointment")
        rows = cursor.fetchall()
        result = " | ".join([f"Patient {pid} with Doctor {did} on {date}" for pid, did, date in rows])
    else:
        result = ""
    
    conn.close()
    return result

def generate_response(user_message: str) -> str:
    db_context = query_doctor_info(user_message)
    prompt = f"Context: {db_context}\nUser: {user_message}\nMedBot:"
    
    inputs = tokenizer.encode(prompt + tokenizer.eos_token, return_tensors="pt")
    outputs = model.generate(
        inputs,
        max_length=200,
        pad_token_id=tokenizer.eos_token_id,
        do_sample=True,
        top_k=50,
        top_p=0.95
    )
    reply = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return reply
