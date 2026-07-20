# Project Documentation

## 1. Architecture Overview

The AI Voice Appointment Booking Agent is built as a modular Streamlit application.

The main application interface and booking workflow are implemented in `app.py`. The application uses session state to manage the conversation, collect appointment details, validate user input, and control the booking flow.

The project is divided into the following components:

- `app.py` manages the user interface, conversation flow, validation, booking confirmation, customer appointment management, and staff dashboard.
- `database/database.py` manages SQLite database connections, table creation, appointment storage, duplicate-slot checks, appointment retrieval, cancellation, and rescheduling.
- `services/speech_service.py` converts recorded voice input into text.
- `services/text_to_speech_service.py` reads the latest agent response aloud.
- `services/email_service.py` sends appointment confirmation emails using SMTP.
- `config.json` stores configurable business information, appointment types, welcome messages, and voice settings.
- `.streamlit/secrets.toml` stores private email credentials locally.
- `.streamlit/secrets.toml.example` provides a safe configuration template for other users.

The application uses SQLite as the local database and Streamlit session state to maintain the current booking conversation.

The main workflow is:

```text
User starts booking
        ↓
Agent collects appointment details
        ↓
Inputs are validated
        ↓
User reviews and confirms the booking
        ↓
Duplicate slot is checked
        ↓
Appointment is saved in SQLite
        ↓
Booking ID is generated
        ↓
Email confirmation is attempted