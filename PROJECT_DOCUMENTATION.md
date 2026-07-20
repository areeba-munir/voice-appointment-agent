# Project Documentation

## 1. Architecture Overview

Write the architecture explanation here:
- `app.py` handles the Streamlit interface and booking flow
- `database/database.py` handles SQLite storage
- `speech_service.py` converts voice to text
- `text_to_speech_service.py` reads responses aloud
- `email_service.py` sends confirmation emails
- `config.json` stores business settings
- Streamlit session state preserves conversation progress

## 2. Features Implemented

Write all completed features here:
- Voice and text booking
- Input validation
- Spoken-email normalization
- Duplicate-slot prevention
- Booking confirmation
- SQLite storage
- Customer lookup
- Customer rescheduling and cancellation
- Staff dashboard
- Search and filters
- CSV export
- Email confirmation support

## 3. Assumptions Made

Write the project assumptions here:
- One confirmed appointment is allowed per date and time slot
- Customers know their Booking ID and contact information
- Cancelled slots can be booked again
- Email delivery is optional
- The app is an English-language prototype
- SQLite is sufficient for the prototype
- Staff authentication is not included

## 4. Challenges Faced

Write the development challenges here:
- Speech recognition sometimes misunderstood short words
- Spoken email addresses needed normalization
- Streamlit reruns required session-state management
- Duplicate slots needed to be prevented
- Customer records needed Booking ID and contact verification
- SMTP authentication needed secure credentials
- GitHub changes caused a merge conflict that had to be resolved

## 5. Future Improvements

Write possible future additions here:
- Staff authentication
- Role-based access
- Cancellation and rescheduling email notifications
- SMS reminders
- Google Calendar integration
- Cloud database
- Multilingual voice support
- Better natural-language understanding
- Business working hours
- Multiple staff/service providers