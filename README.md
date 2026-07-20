# AI Voice Appointment Booking Agent

A Streamlit-based appointment booking prototype that allows users to book, review, reschedule, and cancel appointments using voice or text.

The application also includes a customer self-service page, a staff dashboard, SQLite database storage, CSV export, and email confirmation support.

---

## Live Demo

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://YOUR-APP-NAME.streamlit.app)

## Features

### Appointment Booking

- Book appointments using voice or text
- Speech-to-text transcription
- Review and edit recognized voice input
- Text-to-speech agent responses
- Collect customer name, phone number, email, date, time, appointment type, and reason
- Validate all booking information
- Prevent duplicate appointment slots
- Confirm or cancel the booking before saving
- Generate a Booking ID
- Store confirmed appointments in SQLite

### Customer Appointment Management

Customers can:

- Find an appointment using Booking ID and phone number or email
- View appointment details
- Reschedule a confirmed appointment
- Cancel a confirmed appointment
- View updated appointment status

### Staff Dashboard

Staff can:

- View total, confirmed, cancelled, today, and upcoming appointments
- Search by customer name, phone number, or email
- Filter by status
- Filter by appointment type
- Filter by date
- View appointment records
- Download filtered records as CSV
- Reschedule confirmed appointments
- Cancel confirmed appointments

### Email Confirmation

- Sends a booking confirmation email after a successful appointment
- Uses SMTP settings stored securely in Streamlit secrets
- Shows a user-friendly message if email delivery is unavailable

---

## Technology Stack

- Python
- Streamlit
- SQLite
- Pandas
- Dateparser
- SpeechRecognition
- Streamlit audio input
- pyttsx3
- SMTP
- Git

---

## Project Structure

```text
voice-appointment-agent/
├── .streamlit/
│   ├── secrets.toml
│   └── secrets.toml.example
├── database/
│   ├── __init__.py
│   ├── database.py
│   └── appointments.db
├── services/
│   ├── __init__.py
│   ├── email_service.py
│   ├── speech_service.py
│   └── text_to_speech_service.py
├── app.py
├── config.json
├── requirements.txt
├── README.md
├── TESTING.md
└── .gitignore
```

The following files are local-only and should not be committed:

```text
.streamlit/secrets.toml
database/appointments.db
venv/
__pycache__/
```

---

## Installation

### 1. Clone the repository

Replace `YOUR_GITHUB_REPOSITORY_URL` with the actual repository link.

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd voice-appointment-agent
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

Windows PowerShell:

```powershell
venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```cmd
venv\Scripts\activate
```

macOS or Linux:

```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Email Configuration

A safe example configuration is included in:

```text
.streamlit/secrets.toml.example
```

Create a local file named:

```text
.streamlit/secrets.toml
```

Add valid SMTP credentials:

```toml
[email]
smtp_host = "smtp.gmail.com"
smtp_port = 587
sender_email = "your-email@gmail.com"
sender_password = "your-app-password"
```

For Gmail, use a Gmail App Password instead of the normal account password.

Do not commit the real `secrets.toml` file.

Email delivery is optional. The appointment is still saved if email sending fails.

---

## Run the Application

From the project folder, run:

```bash
python -m streamlit run app.py
```

The application will open in the browser, usually at:

```text
http://localhost:8501
```

---

## Application Pages

### 1. Book Appointment

The user can:

1. Start the booking process
2. Respond using voice or text
3. Review recognized speech
4. Enter booking details
5. Confirm the final appointment
6. Receive a Booking ID
7. Receive an email confirmation when SMTP is configured

The final confirmation commands are:

```text
confirm
cancel
```

### 2. Manage My Appointment

The customer must provide:

- Booking ID
- Phone number or email address used during booking

After successful verification, the customer can:

- View appointment details
- Reschedule the appointment
- Cancel the appointment
- Check appointment status

### 3. Staff Dashboard

The dashboard includes:

- Appointment metrics
- Search and filters
- Appointment records
- CSV export
- Staff rescheduling
- Staff cancellation

---

## Validation Rules

The application validates:

- Full name
- Phone number
- Email address
- Future appointment date
- Future appointment time
- Appointment type
- Appointment reason
- Duplicate appointment slots

Spoken email addresses such as:

```text
name at gmail dot com
```

are normalized into:

```text
name@gmail.com
```

---

## Database

The project uses SQLite.

The database is created automatically when the application starts.

The `appointments` table stores:

- Booking ID
- Full name
- Phone number
- Email address
- Appointment date
- Appointment time
- Appointment type
- Reason
- Status
- Creation timestamp

Appointment statuses include:

```text
Confirmed
Cancelled
```

---

## Testing

Detailed test cases are available in:

```text
TESTING.md
```

Run the following syntax checks:

```bash
python -m py_compile app.py
python -m py_compile database/database.py
```

No output means that no syntax errors were found.

---

## Known Limitations

- Speech-recognition accuracy depends on microphone quality and background noise
- Email delivery requires valid SMTP credentials
- The staff dashboard does not currently include authentication
- SQLite is suitable for this prototype but may not be ideal for a high-traffic production system
- Automatic text-to-speech playback is not enabled to prevent repeated audio during Streamlit reruns

---

## Security Notes

- Never commit real email credentials
- Keep `.streamlit/secrets.toml` in `.gitignore`
- Use `.streamlit/secrets.toml.example` only as a safe template
- Staff authentication and role-based access should be added before production deployment
- Customer appointment lookup requires both Booking ID and matching contact information

---

## Future Improvements

Possible future improvements include:

- Staff login and authentication
- Role-based access control
- Email notifications for cancellation and rescheduling
- SMS notifications
- Google Calendar integration
- Cloud database deployment
- Improved natural-language understanding
- Automatic availability management
- Production-level concurrency controls

---

## Author

**Areeba Munir**
