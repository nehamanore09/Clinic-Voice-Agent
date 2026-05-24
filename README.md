# Clinic Appointment Voice Agent (VAPI + FastAPI + SQLite)

A **voice‑based clinic appointment booking agent** built with **VAPI** (voice telephony), **FastAPI** (backend), and **SQLite** (persistent storage).  
Designed for small clinics: callers can book, cancel, or check clinic hours entirely by voice.

## 🎯 Features

- **Voice calls** handled by **VAPI**: incoming calls, speech‑to‑text, and voice replies.  
- **FastAPI backend** (`main.py`) as the “brain” of the agent.  
- **SQLite database** (`db.sqlite`) stores appointments and prevents double‑booking the same slot.  
- **Clinic‑only replies**: no questions about business, salon, or virtual vs in‑person.  
- **Short, natural responses** with:
  - Clinic name  
  - Confirmation number  
  - Opening hours (Monday–Friday)

## 🧱 Tech Stack

- **Voice layer**: VAPI (handles phone calls, STT, TTS).  
- **Backend**: Python + FastAPI.  
- **Database**: SQLite (file‑based, no server needed).  
- **Tunneling**: ngrok (exposes `localhost:8001` to VAPI during development).

## 📦 Folder Structure

```text
clinic-voice-agent/
├── main.py                    # FastAPI + VAPI webhook + SQLite logic
├── init_db.py                 # Creates db.sqlite with appointments table
├── db.sqlite                  # SQLite database (optional to commit)
├── venv/                      # Python virtual environment
├── requirements.txt           # Dependencies
├── README.md                  # This file
```

## ⚙️ Setup & Run

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/clinic-voice-agent.git
cd clinic-voice-agent
```

### 2. Set up Python environment

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

`requirements.txt` should contain:

```text
fastapi>=0.110.0
uvicorn>=0.29.0
```

### 3. Initialize the SQLite database

```bash
python init_db.py
```

This creates `db.sqlite` with the `appointments` table.

### 4. Start FastAPI server

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8001
```

### 5. Expose the backend with ngrok

In another terminal:

```bash
ngrok http 8001
```

Copy the ngrok URL, e.g.:

```text
https://xxxx.ngrok-free.dev
```

### 6. Connect to VAPI

1. Go to **VAPI dashboard** → **Assistants** → **Create Assistant**.  
2. Choose **Custom Assistant / Custom LLM**.  
3. In **Server Messages URL** or **Server URL**, paste:

   ```text
   https://xxxx.ngrok-free.dev/vapi-webhook
   ```

4. Set the **system prompt** (clinic‑only, short replies):

   ```text
   You are the voice assistant for a small clinic.
   You must only answer questions related to clinic appointments and patient information.
   Speak in short, clear sentences. Do not be robotic or overly formal.
   Do not ask about business, salon, or any non‑clinic topics.
   Do not ask whether the appointment is virtual or in‑person unless explicitly instructed.

   Your task is to:
   1. Greet the caller and ask if they are a new patient or existing patient.
   2. If they want to book an appointment, ask for the day and time (e.g., Monday 10:00) and the doctor's name.
   3. Confirm bookings with clinic name and confirmation number.
   4. If the time is not available, say that it is already booked.

   Keep each reply short (1–2 sentences). Do not add extra information.
   ```

5. Attach a phone number to this assistant and **call it**.

## 📞 Example Call Flow

- **Caller**: “Hi, I want to book an appointment.”  
- **Assistant**: “Thank you for calling Wellness Partners. This is your scheduling assistant. Are you a new patient or existing patient?”  
- **Caller**: “New. I want to book Monday 10:00 with Dr. Sharma.”  
- **Assistant**: “Your appointment is booked for Monday at 10:00 with Dr. Sharma at Wellness Partners. Confirmation number: 12345.”

The appointment is saved in `db.sqlite` and cannot be double‑booked.

## 📊 Data Model (SQLite)

Table `appointments`:

| Column        | Type            | Description                     |
|--------------|-----------------|---------------------------------|
| `id`         | `INTEGER`       | Primary key                    |
| `patient_name`| `TEXT`         | Patient’s name                 |
| `phone`      | `TEXT`         | Patient phone number           |
| `doctor`     | `TEXT`         | Doctor’s name                  |
| `day`        | `TEXT`         | Day of week (e.g., monday)     |
| `time`       | `TEXT`         | Time slot (e.g., 10:00)        |
| `conf_number`| `INTEGER`      | Confirmation number            |
| `created_at` | `DATETIME`     | Inserted automatically         |

Run to inspect:

```bash
python -c "
import sqlite3
conn = sqlite3.connect('db.sqlite')
cur = conn.cursor()
cur.execute('SELECT * FROM appointments;')
for row in cur.fetchall():
    print(row)
"
```

## 🚀 Possible Upgrades

- Add **Google Calendar / n8n** integration so bookings sync with calendars.  
- Add **Docker** for easy deployment.  
- Add a **simple HTML dashboard** to view appointments.  
- Add **authentication** (phone number / token) for secure access.

---

Made with 💡 by Neha Manore.
