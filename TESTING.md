# Testing Report

## 1. Booking Flow Tests

### Test 1: Valid complete booking
- Name: Areeba Munir
- Phone: +923001234567
- Date: Future date
- Time: 2:30 PM
- Type: General Consultation
- Reason: Project discussion
- Confirmation: Yes
- Expected: Appointment saved successfully
- Result:
- Status: Pass / Fail

### Test 2: Invalid name
- Input: A
- Expected: Name rejected
- Result:
- Status: Pass / Fail

### Test 3: Spoken name cleaning
- Input: My name is Sana
- Expected: Saved as Sana
- Result:
- Status: Pass / Fail

### Test 4: Invalid phone
- Input: abc123
- Expected: Phone rejected
- Result:
- Status: Pass / Fail

### Test 5: Valid international phone
- Input: +923001234567
- Expected: Phone accepted
- Result:
- Status: Pass / Fail

### Test 6: Past date
- Input: 2025-01-01
- Expected: Date rejected
- Result:
- Status: Pass / Fail

### Test 7: Natural-language date
- Input: August 2nd 2026
- Expected: Converted to 2026-08-02
- Result:
- Status: Pass / Fail

### Test 8: Ambiguous time
- Input: 2:30
- Expected: Ask for AM or PM
- Result:
- Status: Pass / Fail

### Test 9: Spoken time
- Input: 2:30 p.m.
- Expected: Converted to 02:30 PM
- Result:
- Status: Pass / Fail

### Test 10: 24-hour time
- Input: 
- Expected: Converted to 02:30 PM
- Result:
- Status: Pass / Fail

### Test 11: Duplicate slot
- Input: Same date and time as an existing appointment
- Expected: Appointment rejected and another time requested
- Result:
- Status: Pass / Fail


### Test 12: Cancellation
- Input: Cancel my appointment
- Expected: Booking cancelled and temporary data cleared
- Result:
- Status: Pass / Fail

### Test 13: Rejection at confirmation
- Input: Details are wrong
- Expected: Booking restarts
- Result:
- Status: Pass / Fail
### Test 14: Voice input
- Input: Record a clear response
- Expected: Speech converted to text and processed
- Result:
- Status: Pass / Fail

### Test 15: Voice failure fallback
- Input: Silent or unclear recording
- Expected: Error shown and text input remains available
- Result:
- Status: Pass / Fail

## 2. Database Tests

### Test 16: Persistence
- Action: Restart Streamlit
- Expected: Saved appointments remain
- Result:
- Status: Pass / Fail

### Test 17: Booking ID
- Expected: Every saved appointment has a unique ID
- Result:
- Status: Pass / Fail

### Test 18: Stored fields
- Expected: Name, phone, date, time, type, reason, status, created time stored
- Result:
- Status: Pass / Fail

## 3. Dashboard Tests

### Test 19: Navigation
- Expected: Both pages open correctly
- Result:
- Status: Pass / Fail

### Test 20: Metrics
- Expected: Total, Confirmed, Today, and Upcoming values are correct
- Result:
- Status: Pass / Fail

### Test 21: Search
- Expected: Search by name and phone works
- Result:
- Status: Pass / Fail

### Test 22: Status filter
- Expected: Status filter shows matching rows
- Result:
- Status: Pass / Fail

### Test 23: Type filter
- Expected: Appointment-type filter works
- Result:
- Status: Pass / Fail

### Test 24: Date filter
- Expected: Only appointments from the selected date appear
- Result:
- Status: Pass / Fail

### Test 25: CSV export
- Expected: Download contains only filtered records
- Result:
- Status: Pass / Fail14:30