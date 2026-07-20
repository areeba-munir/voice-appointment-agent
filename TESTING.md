# Testing Report

## Project

AI Voice Appointment Booking Agent

## Testing Environment

- Operating System: Windows
- Python: 3.x
- Framework: Streamlit
- Database: SQLite
- Browser: Google Chrome

## Test Cases

| Test ID | Feature | Test Steps | Expected Result | Status |
|---|---|---|---|---|
| T01 | Start booking | Click Start Appointment Booking | Agent asks for full name | Pass |
| T02 | Valid name | Enter a valid full name | Name is accepted | Pass |
| T03 | Invalid name | Enter numbers or a very short name | Validation message appears | Pass |
| T04 | Phone validation | Enter a valid phone number | Phone is normalized and accepted | Pass |
| T05 | Invalid phone | Enter letters or an invalid-length number | Validation message appears | Pass |
| T06 | Email validation | Enter a valid email address | Email is accepted | Pass |
| T07 | Spoken email | Say email using “at” and “dot” | Email is normalized | Pass |
| T08 | Invalid email | Enter an invalid email | Validation message appears | Pass |
| T09 | Future date | Enter a future date | Date is accepted | Pass |
| T10 | Past date | Enter a past date | Validation message appears | Pass |
| T11 | Valid time | Enter a valid future time | Time is accepted | Pass |
| T12 | Past time today | Enter a time that has passed | Validation message appears | Pass |
| T13 | Appointment type | Select an available appointment type | Type is accepted | Pass |
| T14 | Reason | Enter a valid reason | Reason is accepted | Pass |
| T15 | Confirm booking | Enter “confirm” | Appointment is saved | Pass |
| T16 | Cancel during booking | Enter “cancel” | Booking stops without saving | Pass |
| T17 | Duplicate slot | Book the same date and time twice | Duplicate warning appears | Pass |
| T18 | Voice transcription | Record and convert speech to text | Recognized text appears for review | Pass |
| T19 | Edit transcription | Correct recognized text | Corrected value is used | Pass |
| T20 | Email confirmation | Complete booking with valid email settings | Confirmation email is sent | Pass/Not Configured |
| T21 | Customer lookup | Enter correct Booking ID and contact | Appointment details appear | Pass |
| T22 | Invalid customer lookup | Enter wrong contact information | No appointment details appear | Pass |
| T23 | Customer reschedule | Select a new free date and time | Appointment is updated | Pass |
| T24 | Customer cancel | Confirm cancellation | Status changes to Cancelled | Pass |
| T25 | Cancelled appointment controls | Open a cancelled appointment | Reschedule and cancel controls are hidden | Pass |
| T26 | Dashboard records | Open management dashboard | Appointment records appear | Pass |
| T27 | Search | Search by name, phone, or email | Matching records appear | Pass |
| T28 | Status filter | Filter by Confirmed or Cancelled | Correct records appear | Pass |
| T29 | Type filter | Filter by appointment type | Correct records appear | Pass |
| T30 | Date filter | Select an appointment date | Correct records appear | Pass |
| T31 | CSV export | Click Download Filtered Appointments | CSV file downloads | Pass |
| T32 | Admin reschedule | Reschedule a confirmed appointment | Date and time update | Pass |
| T33 | Admin cancel | Cancel a confirmed appointment | Status changes to Cancelled | Pass |
| T34 | Reset application | Click Reset Application | Booking state is cleared | Pass |

## Syntax Testing

The following commands were used:

```bash
python -m py_compile app.py
python -m py_compile database/database.py