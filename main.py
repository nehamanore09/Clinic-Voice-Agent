# main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import sqlite3
import random

app = FastAPI()

CLINIC_NAME = "Wellness Partners"
DOCTOR_NAMES = ["Dr. Sharma", "Dr. Patel", "Dr. Gupta", "Dr. Mehta"]

SCHEDULE = {
    "monday": ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"],
    "tuesday": ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"],
    "wednesday": ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"],
    "thursday": ["09:00", "10:00", "11:00", "14:00", "15:00"],
    "friday": ["09:00", "10:00", "11:00", "14:00", "15:00"],
}

hours = (
    "We are open Monday to Friday, from 9 AM to 11 AM and from 2 PM to 5 PM."
)


def get_db_conn():
    return sqlite3.connect("db.sqlite")


@app.get("/")
def home():
    return {"status": "clinic voice agent backend is running"}


@app.post("/vapi-webhook")
async def vapi_webhook(request: Request):
    data = await request.json()
    message = data.get("message", {}).get("content", "").lower().strip()

    print("VAPI → message:", message)

    # Very simple parser for patient name and phone
    # In real project you’d use an NLP model or more robust parsing
    patient_name = None
    phone = None
    doctor = None

    for d in DOCTOR_NAMES:
        if d.lower() in message:
            doctor = d

    # Assume "neha 24 year old" etc. → just say "my name is ..."
    if "name is" in message:
        words = message.split("name is")
        if len(words) > 1:
            patient_name = words[1].strip().split()[0].title()

    if "phone" in message or "number" in message:
        # assume caller says a 10‑digit phone somewhere
        # in prod you’d extract numbers with regex
        phone = "xxxx‑xxxxxx"  # placeholder

    # Logic
    if "hello" in message or "hi" in message:
        reply = (
            f"Thank you for calling {CLINIC_NAME}. "
            "This is your scheduling assistant. "
            "Are you a new patient or existing patient?"
        )
    elif "new" in message:
        reply = (
            "Thank you. Please tell me your name and phone number, "
            "and the doctor you want to see."
        )
    elif "existing" in message:
        reply = (
            "Thank you. Please tell me your phone number and the doctor you want to see."
        )
    elif "book" in message:
        reply = (
            f"To book an appointment, please tell me the day and time, "
            f"for example: Monday 10:00. {hours}"
        )

    else:
        booked = False
        day_found = None
        time_found = None

        for day, slots in SCHEDULE.items():
            if day in message:
                day_found = day
                for slot in slots:
                    if slot in message:
                        time_found = slot

                        # Check if already booked in DB
                        conn = get_db_conn()
                        cur = conn.cursor()
                        cur.execute(
                            "SELECT * FROM appointments WHERE day = ? AND time = ?",
                            (day, slot)
                        )
                        existing = cur.fetchone()
                        if existing:
                            reply = "Sorry, that time is already booked. Please choose another."
                        else:
                            conf_num = random.randint(10000, 99999)
                            try:
                                cur.execute(
                                    "INSERT INTO appointments (patient_name, phone, doctor, day, time, conf_number) VALUES (?, ?, ?, ?, ?, ?)",
                                    (patient_name or "Unknown", phone, doctor or "General", day, slot, conf_num),
                                )
                                conn.commit()  # critical!
                                print("✅ Booking saved in DB:", day, slot, conf_num)
                                if doctor:
                                    reply = (
                                        f"Your appointment is booked for {day.capitalize()} "
                                        f"at {slot} with {doctor} at {CLINIC_NAME}. "
                                        f"Confirmation number: {conf_num}."
                                    )
                                else:
                                    reply = (
                                        f"Your appointment is booked for {day.capitalize()} "
                                        f"at {slot} at {CLINIC_NAME}. "
                                        f"Confirmation number: {conf_num}."
                                    )
                            except Exception as e:
                                conn.rollback()  # in case of error
                                print("❌ DB error:", str(e))
                                reply = "Sorry, we could not save the booking right now. Please try again."
                        conn.close()
                        booked = True
                        break
                if booked:
                    break

        if not booked:
            reply = (
                f"Please say: new patient, existing patient, or book "
                f"with a day and time, for example: Monday 10:00. {hours}"
            )


    return JSONResponse({
        "message": {
            "role": "assistant",
            "content": reply
        }
    })
