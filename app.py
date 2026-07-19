import json
import re
from datetime import datetime
import dateparser

import pandas as pd
import streamlit as st

import importlib
from database import database as db

# Force Python/Streamlit to reload the latest saved database.py
importlib.invalidate_caches()
db = importlib.reload(db)

appointment_exists = db.appointment_exists
cancel_appointment = db.cancel_appointment
get_all_appointments = db.get_all_appointments
initialize_database = db.initialize_database
reschedule_appointment = db.reschedule_appointment
save_appointment = db.save_appointment

from services.speech_service import transcribe_audio
from services.text_to_speech_service import speak_text

# ---------------------------------------------------
# Page configuration
# ---------------------------------------------------
st.set_page_config(
    page_title="AI Voice Appointment Agent",
    page_icon="📅",
    layout="wide"
)


# ---------------------------------------------------
# Load business configuration
# ---------------------------------------------------
def load_config() -> dict:
    """Load application settings from config.json."""
    try:
        with open("config.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        st.error("config.json was not found.")
        st.stop()
    except json.JSONDecodeError:
        st.error("config.json contains invalid JSON.")
        st.stop()


config = load_config()
initialize_database()

# ---------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------
page = st.sidebar.radio(
    "Navigation",
    [
        "Book Appointment",
        "Manage Appointments"
    ]
)

# ---------------------------------------------------
# Manage appointments page
# ---------------------------------------------------
if page == "Manage Appointments":
    st.title("📊 Appointment Management Dashboard")
    st.caption(config["business_name"])

    appointments = get_all_appointments()

    if not appointments:
        st.info("No appointments have been stored yet.")
        st.stop()

    appointments_df = pd.DataFrame(appointments)

    # Convert appointment date into datetime format
    appointments_df["appointment_date"] = pd.to_datetime(
        appointments_df["appointment_date"],
        errors="coerce"
    )

    # Calculate dashboard metrics
    today = pd.Timestamp.now().normalize()

    total_appointments = len(appointments_df)

    confirmed_appointments = len(
        appointments_df[
            appointments_df["status"] == "Confirmed"
        ]
    )

    today_appointments = len(
        appointments_df[
            appointments_df["appointment_date"] == today
        ]
    )

    upcoming_appointments = len(
        appointments_df[
            appointments_df["appointment_date"] > today
        ]
    )

    # Display dashboard cards
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

    with metric_col1:
        st.metric(
            label="Total Appointments",
            value=total_appointments
        )

    with metric_col2:
        st.metric(
            label="Confirmed",
            value=confirmed_appointments
        )

    with metric_col3:
        st.metric(
            label="Today's Appointments",
            value=today_appointments
        )

    with metric_col4:
        st.metric(
            label="Upcoming",
            value=upcoming_appointments
        )

    st.divider()

    # ---------------------------------------------------
    # Appointment filters
    # ---------------------------------------------------
    st.subheader("Filter Appointments")

    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)

    with filter_col1:
        search_name = st.text_input(
            "Search by name or phone number"
        )

    with filter_col2:
        selected_status = st.selectbox(
            "Filter by status",
            ["All", "Confirmed"]
        )

    with filter_col3:
        selected_type = st.selectbox(
            "Filter by appointment type",
            ["All"] + config["appointment_types"]
        )

    with filter_col4:
        selected_date = st.date_input(
            "Filter by date",
            value=None
        )

    # Create a copy for filtering
    filtered_df = appointments_df.copy()

    if search_name:
        search_text = search_name.strip().lower()

        filtered_df = filtered_df[
            filtered_df["full_name"].str.lower().str.contains(
                search_text,
                na=False
            )
            |
            filtered_df["phone_number"].astype(str).str.contains(
                search_text,
                na=False
            )
        ]

    if selected_status != "All":
        filtered_df = filtered_df[
            filtered_df["status"] == selected_status
        ]

    if selected_type != "All":
        filtered_df = filtered_df[
            filtered_df["appointment_type"] == selected_type
        ]

    if selected_date is not None:
        selected_timestamp = pd.Timestamp(selected_date)

        filtered_df = filtered_df[
            filtered_df["appointment_date"] == selected_timestamp
        ]

    st.write(
        f"Showing **{len(filtered_df)}** of "
        f"**{len(appointments_df)}** appointments."
    )

    st.divider()

    # Convert date back into readable text
    filtered_df["appointment_date"] = (
        filtered_df["appointment_date"]
        .dt.strftime("%Y-%m-%d")
    )

    # Rename table columns
    filtered_df = filtered_df.rename(
        columns={
            "id": "Booking ID",
            "full_name": "Full Name",
            "phone_number": "Phone Number",
            "appointment_date": "Date",
            "appointment_time": "Time",
            "appointment_type": "Appointment Type",
            "reason": "Reason",
            "status": "Status",
            "created_at": "Created At"
        }
    )

    st.subheader("Appointment Records")

    csv_data = filtered_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="⬇️ Download Filtered Appointments",
        data=csv_data,
        file_name="appointments.csv",
        mime="text/csv"
    )

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )

    # ---------------------------------------------------
    # Reschedule a saved appointment
    # ---------------------------------------------------
    st.divider()
    st.subheader("Reschedule an Appointment")

    if "reschedule_success_message" in st.session_state:
        st.success(st.session_state.reschedule_success_message)
        del st.session_state.reschedule_success_message

    confirmed_reschedule_df = appointments_df[
        appointments_df["status"] == "Confirmed"
    ].copy()

    if confirmed_reschedule_df.empty:
        st.info(
            "There are no confirmed appointments available to reschedule."
        )

    else:
        reschedule_options = {}

        for _, appointment_row in confirmed_reschedule_df.iterrows():
            option_label = (
                f"Booking #{appointment_row['id']} — "
                f"{appointment_row['full_name']} — "
                f"{appointment_row['appointment_date'].strftime('%Y-%m-%d')} "
                f"at {appointment_row['appointment_time']}"
            )

            reschedule_options[option_label] = int(
                appointment_row["id"]
            )

        selected_reschedule_appointment = st.selectbox(
            "Select a confirmed appointment to reschedule",
            options=list(reschedule_options.keys()),
            key="reschedule_appointment_select"
        )

        new_date = st.date_input(
            "Select a new appointment date",
            min_value=datetime.now().date(),
            key="reschedule_date"
        )

        new_time = st.time_input(
            "Select a new appointment time",
            key="reschedule_time"
        )

        confirm_reschedule = st.checkbox(
            "I confirm that I want to reschedule this appointment.",
            key="confirm_reschedule"
        )

        if st.button(
            "Reschedule Selected Appointment",
            type="primary",
            disabled=not confirm_reschedule
        ):
            selected_appointment_id = reschedule_options[
                selected_reschedule_appointment
            ]

            formatted_date = new_date.strftime("%Y-%m-%d")
            formatted_time = new_time.strftime("%I:%M %p")

            if appointment_exists(
                formatted_date,
                formatted_time
            ):
                st.error(
                    "That date and time are already booked. "
                    "Please choose another slot."
                )

            else:
                reschedule_successful = reschedule_appointment(
                    selected_appointment_id,
                    formatted_date,
                    formatted_time
                )

                if reschedule_successful:
                    st.session_state.reschedule_success_message = (
                         f"Booking #{selected_appointment_id} "
                         f"has been rescheduled successfully to "
                         f"{formatted_date} at {formatted_time}."
                  )
                    st.rerun()

                else:
                    st.error(
                        "The appointment could not be rescheduled. "
                        "It may already be cancelled."
                    )

    # ---------------------------------------------------
    # Cancel a saved appointment
    # ---------------------------------------------------
    st.divider()
    st.subheader("Cancel an Appointment")

    confirmed_appointments_df = appointments_df[
        appointments_df["status"] == "Confirmed"
    ].copy()

    if confirmed_appointments_df.empty:
        st.info("There are no confirmed appointments available to cancel.")

    else:
        cancellation_options = {}

        for _, appointment_row in confirmed_appointments_df.iterrows():
            option_label = (
                f"Booking #{appointment_row['id']} — "
                f"{appointment_row['full_name']} — "
                f"{appointment_row['appointment_date'].strftime('%Y-%m-%d')} "
                f"at {appointment_row['appointment_time']}"
            )

            cancellation_options[option_label] = int(
                appointment_row["id"]
            )

        selected_appointment = st.selectbox(
            "Select a confirmed appointment",
            options=list(cancellation_options.keys())
        )

        confirm_cancellation = st.checkbox(
            "I confirm that I want to cancel this appointment."
        )

        if st.button(
            "Cancel Selected Appointment",
            type="primary",
            disabled=not confirm_cancellation
        ):
            selected_appointment_id = cancellation_options[
                selected_appointment
            ]

            cancellation_successful = cancel_appointment(
                selected_appointment_id
            )

            if cancellation_successful:
                st.success(
                    f"Booking #{selected_appointment_id} "
                    "has been cancelled successfully."
                )
                st.rerun()

            else:
                st.error(
                    "The appointment could not be cancelled. "
                    "It may already be cancelled."
                )

  

    st.stop()


st.title("📅 AI Appointment Booking Agent")
st.caption(config["business_name"])

st.info(
    "Book an appointment using voice or text. "
    "All confirmed appointments are saved automatically."
)

# ---------------------------------------------------
# Session state initialization
# ---------------------------------------------------
default_state = {
    "booking_started": False,
    "current_field": "full_name",
    "appointment": {
        "full_name": "",
        "phone_number": "",
        "appointment_date": "",
        "appointment_time": "",
        "appointment_type": "",
        "reason": ""
    },
    "messages": [
        {
            "role": "assistant",
            "content": config["welcome_message"]
        }
    ],
    "awaiting_confirmation": False,
    "booking_completed": False,
    "appointment_id": None,
    "voice_input_key": 0,
    "editing_field": None,
    "pending_voice_text": None
}

for key, value in default_state.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ---------------------------------------------------
# Validation functions
# ---------------------------------------------------
def validate_name(name: str) -> tuple[bool, str]:
    cleaned_name = name.strip()

    if not cleaned_name:
        return False, "Name cannot be empty."

    # Remove common spoken introductions
    spoken_prefixes = [
        r"^my name is\s+",
        r"^i am\s+",
        r"^i'm\s+",
        r"^this is\s+",
        r"^you can call me\s+"
    ]

    for prefix in spoken_prefixes:
        cleaned_name = re.sub(
            prefix,
            "",
            cleaned_name,
            flags=re.IGNORECASE
        )

    cleaned_name = cleaned_name.strip()

    if len(cleaned_name) < 3:
        return False, "Please enter your complete name."

    if not re.fullmatch(r"[A-Za-z\s.'-]+", cleaned_name):
        return False, "Name should contain letters only."

    return True, cleaned_name.title()


def validate_phone(phone: str) -> tuple[bool, str]:
    phone = phone.strip()

    if not phone:
        return False, "Phone number cannot be empty."

    cleaned_phone = re.sub(r"[\s\-()]", "", phone)

    if cleaned_phone.startswith("+"):
        digits = cleaned_phone[1:]
    else:
        digits = cleaned_phone

    if not digits.isdigit():
        return False, "Please enter a valid phone number."

    if len(digits) < 10 or len(digits) > 15:
        return False, "Phone number must contain between 10 and 15 digits."

    return True, cleaned_phone


def validate_date(date_text: str) -> tuple[bool, str]:
    cleaned_date = date_text.strip()

    if not cleaned_date:
        return False, "Appointment date cannot be empty."

    parsed_date = None

    # Accept typed dates only in the unambiguous ISO format
    try:
        parsed_date = datetime.strptime(
            cleaned_date,
            "%Y-%m-%d"
        ).date()

    except ValueError:
        # Natural-language parsing is only used when letters are present,
        # such as "9 September 2026" or "next Monday".
        if re.search(r"[A-Za-z]", cleaned_date):
            parsed_datetime = dateparser.parse(
                cleaned_date,
                languages=["en"],
                settings={
                    "DATE_ORDER": "DMY",
                    "PREFER_DATES_FROM": "future",
                    "STRICT_PARSING": False
                }
            )

            if parsed_datetime is not None:
                parsed_date = parsed_datetime.date()

    if parsed_date is None:
        return False, (
            "Please enter the date in YYYY-MM-DD format, "
            "or say the full date naturally, such as "
            "9 September 2026."
        )

    if parsed_date < datetime.now().date():
        return False, "Please choose today or a future date."

    return True, parsed_date.strftime("%Y-%m-%d")

def validate_time(time_text: str) -> tuple[bool, str]:
    cleaned_time = time_text.strip().upper()

    if not cleaned_time:
        return False, "Time cannot be empty."

    # Speech recognition may return P.M. or A.M.
    cleaned_time = cleaned_time.replace(".", "")

    # Remove common spoken words
    cleaned_time = re.sub(
        r"\b(AT|OCLOCK|O CLOCK)\b",
        "",
        cleaned_time
    )

    cleaned_time = re.sub(r"\s+", " ", cleaned_time).strip()

    # Convert speech such as "23 23" into "23:23"
    # Also converts "14 30" into "14:30"
    if re.fullmatch(r"\d{1,2}\s+\d{1,2}", cleaned_time):
        hour_text, minute_text = cleaned_time.split()

        hour = int(hour_text)
        minute = int(minute_text)

        if 0 <= hour <= 23 and 0 <= minute <= 59:
            cleaned_time = f"{hour:02d}:{minute:02d}"
        else:
            return False, (
                "That time is invalid. "
                "Use a valid time such as 14:30 or 2:30 PM."
            )

    # Convert a single 24-hour value such as 14 into 14:00
    if re.fullmatch(r"\d{1,2}", cleaned_time):
        hour = int(cleaned_time)

        if 13 <= hour <= 23:
            cleaned_time = f"{hour:02d}:00"

        elif hour == 0:
            cleaned_time = "00:00"

        elif 1 <= hour <= 12:
            return False, (
                "Please specify AM or PM, for example 2 PM, "
                "or use 24-hour format such as 14."
            )

        else:
            return False, "The hour must be between 0 and 23."

    # Convert 2:30PM into 2:30 PM
    cleaned_time = re.sub(
        r"\s*(AM|PM)$",
        r" \1",
        cleaned_time
    )

    # Ask for AM/PM when a 12-hour value is ambiguous
    if re.fullmatch(r"\d{1,2}:\d{2}", cleaned_time):
        hour = int(cleaned_time.split(":")[0])

        if 1 <= hour <= 12:
            return False, (
                "Please specify AM or PM, for example 2:30 PM, "
                "or use 24-hour format such as 14:30."
            )

    supported_formats = [
        "%H:%M",
        "%I:%M %p",
        "%I %p"
    ]

    parsed_time = None

    for time_format in supported_formats:
        try:
            parsed_time = datetime.strptime(
                cleaned_time,
                time_format
            ).time()
            break
        except ValueError:
            continue

    if parsed_time is None:
        return False, (
            "I could not understand that time. "
            "Try saying 2:30 PM, 14:30, or 14."
        )

    selected_date_text = st.session_state.appointment.get(
        "appointment_date",
        ""
    )

    if selected_date_text:
        try:
            selected_date = datetime.strptime(
                selected_date_text,
                "%Y-%m-%d"
            ).date()
        except ValueError:
            return False, "The selected appointment date is invalid."

        if selected_date == datetime.now().date():
            if parsed_time <= datetime.now().time():
                return False, (
                    "That time has already passed. "
                    "Please choose a future time."
                )

    return True, parsed_time.strftime("%I:%M %p")


def normalize_message(message: str) -> str:
    """Convert user input into a simpler format for intent checking."""
    message = message.lower().strip()
    message = re.sub(r"[^\w\s]", "", message)
    message = re.sub(r"\s+", " ", message)
    return message


def is_cancellation_message(message: str) -> bool:
    normalized_message = normalize_message(message)

    cancellation_phrases = [
        "cancel",
        "cancel booking",
        "cancel appointment",
        "stop",
        "quit",
        "exit",
        "never mind",
        "nevermind",
        "i dont want to continue",
        "i do not want to continue",
        "do not book",
        "dont book"
    ]

    return any(
        phrase == normalized_message
        or phrase in normalized_message
        for phrase in cancellation_phrases
    )


def is_confirmation(message: str) -> bool:
    normalized_message = normalize_message(message)

    confirmation_phrases = [
        "yes",
        "y",
        "confirm",
        "confirmed",
        "proceed",
        "book it",
        "book appointment",
        "yes confirm",
        "yes proceed",
        "yes please",
        "okay",
        "ok",
        "sure",
        "correct",
        "details are correct"
    ]

    return normalized_message in confirmation_phrases


def is_rejection(message: str) -> bool:
    normalized_message = normalize_message(message)

    rejection_phrases = [
        "no",
        "n",
        "change",
        "edit",
        "incorrect",
        "not correct",
        "details are wrong",
        "restart",
        "start again",
        "no restart",
        "i want to change"
    ]

    return normalized_message in rejection_phrases

# ---------------------------------------------------
# Edit command detection
# ---------------------------------------------------
def get_requested_edit_field(message: str) -> str | None:
    """Detect which appointment detail the user wants to change."""
    normalized_message = normalize_message(message)

    edit_words = (
        "change",
        "edit",
        "correct",
        "update",
        "replace"
    )

    if not any(word in normalized_message for word in edit_words):
        return None

    if "name" in normalized_message:
        return "full_name"

    if "phone" in normalized_message or "number" in normalized_message:
        return "phone_number"

    if "date" in normalized_message:
        return "appointment_date"

    if "time" in normalized_message:
        return "appointment_time"

    if (
        "appointment type" in normalized_message
        or "booking type" in normalized_message
        or normalized_message.endswith("type")
    ):
        return "appointment_type"

    if "reason" in normalized_message or "purpose" in normalized_message:
        return "reason"

    return None


# ---------------------------------------------------
# Conversation questions
# ---------------------------------------------------
questions = {
    "full_name": "What is your full name?",
    "phone_number": "What is your phone number?",
    "appointment_date": (
        "Please provide your preferred appointment date. "
        "Enter it in YYYY-MM-DD format or state the full date in words."
    ),
    "appointment_time": (
        "What time would you prefer? "
        "For example, 2:30 PM or 14:30."
    ),
    "appointment_type": "Please select an appointment type.",
    "reason": "What is the reason or purpose of your appointment?"
}

field_order = [
    "full_name",
    "phone_number",
    "appointment_date",
    "appointment_time",
    "appointment_type",
    "reason"
]
field_labels = {
    "full_name": "Name",
    "phone_number": "Phone Number",
    "appointment_date": "Appointment Date",
    "appointment_time": "Appointment Time",
    "appointment_type": "Appointment Type",
    "reason": "Reason"
}


# ---------------------------------------------------
# Helper functions
# ---------------------------------------------------
def add_message(role: str, content: str) -> None:
    st.session_state.messages.append(
        {
            "role": role,
            "content": content
        }
    )

def begin_edit(field: str) -> None:
    """Start editing one appointment field."""
    st.session_state.editing_field = field
    st.session_state.current_field = field
    st.session_state.awaiting_confirmation = False
    st.session_state.voice_input_key += 1
    st.session_state.pending_voice_text = None

    add_message(
        "assistant",
        f"Please enter the correct "
        f"{field_labels[field].lower()}."
    )


def render_appointment_details() -> None:
    """Display completed appointment details with edit buttons."""
    filled_fields = [
        field
        for field in field_order
        if st.session_state.appointment.get(field)
    ]

    if not filled_fields:
        return

    with st.container(border=True):
        st.markdown("### Your Appointment Details")

        if st.session_state.editing_field:
            editing_label = field_labels[
                st.session_state.editing_field
            ]

            st.info(
                f"You are editing **{editing_label}**. "
                "Enter the corrected value below."
            )

        for field in filled_fields:
            detail_column, edit_column = st.columns([5, 1])

            with detail_column:
                st.markdown(
                    f"**{field_labels[field]}:** "
                    f"{st.session_state.appointment[field]}"
                )

            with edit_column:
                st.button(
                    "Edit",
                    key=f"edit_detail_{field}",
                    on_click=begin_edit,
                    args=(field,),
                    disabled=(
                        st.session_state.editing_field
                        is not None
                    ),
                    use_container_width=True
                )
def get_latest_assistant_message() -> str:
    """Return the latest assistant response from conversation history."""

    for message in reversed(st.session_state.messages):
        if message["role"] == "assistant":
            return message["content"]

    return ""

def reset_booking() -> None:
    st.session_state.booking_started = False
    st.session_state.current_field = "full_name"
    st.session_state.appointment = {
        "full_name": "",
        "phone_number": "",
        "appointment_date": "",
        "appointment_time": "",
        "appointment_type": "",
        "reason": ""
    }
    st.session_state.awaiting_confirmation = False
    st.session_state.booking_completed = False
    st.session_state.appointment_id = None
    st.session_state.editing_field = None
    st.session_state.pending_voice_text = None
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": config["welcome_message"]
        }
    ]


def move_to_next_field() -> None:
    current_field = st.session_state.current_field
    current_index = field_order.index(current_field)

    if current_index < len(field_order) - 1:
        next_field = field_order[current_index + 1]
        st.session_state.current_field = next_field
        add_message("assistant", questions[next_field])
    else:
        st.session_state.awaiting_confirmation = True

        appointment = st.session_state.appointment

        confirmation_message = f"""
Please confirm your appointment details:

**Name:** {appointment["full_name"]}  
**Phone:** {appointment["phone_number"]}  
**Date:** {appointment["appointment_date"]}  
**Time:** {appointment["appointment_time"]}  
**Appointment Type:** {appointment["appointment_type"]}  
**Reason:** {appointment["reason"]}

Type **yes** to confirm or **no** to cancel this booking.
"""

        add_message("assistant", confirmation_message)


def process_field(field: str, user_input: str) -> None:
    user_input = user_input.strip()

    if not user_input:
        add_message(
            "assistant",
            "I did not receive a response. "
            "Please enter the requested information."
        )
        return

    if field == "full_name":
        valid, result = validate_name(user_input)

    elif field == "phone_number":
        valid, result = validate_phone(user_input)

    elif field == "appointment_date":
        valid, result = validate_date(user_input)

    elif field == "appointment_time":
        valid, result = validate_time(user_input)

    elif field == "appointment_type":
        valid = user_input in config["appointment_types"]
        result = (
            user_input
            if valid
            else "Please select one of the available appointment types."
        )

    elif field == "reason":
        valid = len(user_input.strip()) >= 3
        result = (
            user_input.strip()
            if valid
            else "Please provide a valid reason for the appointment."
        )

    else:
        valid = False
        result = "Unknown booking field."

    if not valid:
        add_message("assistant", result)
        return

    st.session_state.appointment[field] = result
    st.session_state.last_answered_field = field

    # If the user is editing an already accepted field
    if st.session_state.editing_field == field:
        st.session_state.editing_field = None

        add_message(
            "assistant",
             f"{field_labels[field]} updated successfully."
        )

        # Continue from the first field that is still empty
        for pending_field in field_order:
            if not st.session_state.appointment[pending_field]:
                st.session_state.current_field = pending_field

                add_message(
                    "assistant",
                    questions[pending_field]
                )
                break

        # If no fields are empty, return to confirmation
        else:
            st.session_state.awaiting_confirmation = True

            appointment = st.session_state.appointment

            confirmation_message = f"""
Please confirm your appointment details:

**Name:** {appointment["full_name"]}  
**Phone:** {appointment["phone_number"]}  
**Date:** {appointment["appointment_date"]}  
**Time:** {appointment["appointment_time"]}  
**Appointment Type:** {appointment["appointment_type"]}  
**Reason:** {appointment["reason"]}

Type **yes** to confirm or **no** to cancel this booking.
"""

            add_message(
                "assistant",
                confirmation_message
            )

    else:
        move_to_next_field()


# ---------------------------------------------------
# Display conversation
# ---------------------------------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


latest_agent_message = get_latest_assistant_message()

voice_settings = config.get("voice_settings", {})

voice_enabled = voice_settings.get("enabled", True)

if latest_agent_message and voice_enabled:
    if st.button("🔊 Speak Agent Response"):
        success, result = speak_text(
            latest_agent_message,
            rate=voice_settings.get("rate", 165),
            volume=voice_settings.get("volume", 1.0)
        )

        if not success:
            st.error(result)




# ---------------------------------------------------
# Start booking button
# ---------------------------------------------------
if not st.session_state.booking_started:
    if st.button("Start Appointment Booking", type="primary"):
        st.session_state.booking_started = True
        add_message("assistant", questions["full_name"])
        st.rerun()


# ---------------------------------------------------
# Appointment type selector
# ---------------------------------------------------
elif (
    st.session_state.current_field == "appointment_type"
    and not st.session_state.awaiting_confirmation
):
    selected_type = st.selectbox(
        "Appointment Type",
        options=["Select an option"] + config["appointment_types"]
    )

    if st.button("Submit Appointment Type"):
        if selected_type == "Select an option":
            add_message(
                "assistant",
                "Please select an appointment type."
            )
        else:
            add_message("user", selected_type)
            process_field("appointment_type", selected_type)

        st.rerun()


# ---------------------------------------------------
# Chat input
# ---------------------------------------------------
elif not st.session_state.booking_completed:
    st.markdown("#### Respond by voice or text")

    voice_input = None
    text_input = None

    # Show recorder only when no transcription is awaiting review
    if st.session_state.pending_voice_text is None:
        recorded_audio = st.audio_input(
            "Record your response",
            sample_rate=16000,
            key=f"booking_voice_{st.session_state.voice_input_key}"
        )

        if recorded_audio is not None:
            if st.button(
                "Convert Voice to Text",
                key=f"voice_button_{st.session_state.voice_input_key}"
            ):
                with st.spinner("Converting your voice to text..."):
                    success, result = transcribe_audio(recorded_audio)

                if success:
                    st.session_state.pending_voice_text = result
                    st.rerun()
                else:
                    st.error(result)

        text_input = st.chat_input(
            "Or type your response here..."
        )

    # Let user review and correct recognized speech
    else:
        st.info(
             "Review the recognized text below. "
             "You can correct it manually or record your response again."
        )

        reviewed_voice_text = st.text_input(
            "Recognized text",
            value=st.session_state.pending_voice_text,
            key=f"reviewed_voice_{st.session_state.voice_input_key}"
        )

        confirm_col, retry_col = st.columns(2)

        with confirm_col:
            confirm_voice = st.button(
                "✅ Confirm Response",
                type="primary",
                use_container_width=True
            )

        with retry_col:
            retry_voice = st.button(
                "🔄 Record Again",
                use_container_width=True
            )

        if confirm_voice:
            if reviewed_voice_text.strip():
                voice_input = reviewed_voice_text.strip()
                st.session_state.pending_voice_text = None
            else:
                st.error(
                    "The response cannot be empty."
                )

        if retry_voice:
            st.session_state.pending_voice_text = None
            st.session_state.voice_input_key += 1
            st.rerun()

    user_input = text_input or voice_input


    if user_input:
        add_message("user", user_input)
        requested_edit_field = get_requested_edit_field(user_input)
        
        if requested_edit_field:
            st.session_state.editing_field = requested_edit_field
            st.session_state.current_field = requested_edit_field
            st.session_state.awaiting_confirmation = False
            
            add_message(
                 "assistant",
                 f"Sure. {questions[requested_edit_field]}"
            )

            st.session_state.voice_input_key += 1
            st.rerun()

        if is_cancellation_message(user_input):
            add_message(
                "assistant",
                "Your appointment booking has been cancelled. "
                "You can start a new booking whenever you are ready."
            )

            st.session_state.booking_started = False
            st.session_state.current_field = "full_name"
            st.session_state.awaiting_confirmation = False
            st.session_state.booking_completed = False
            st.session_state.appointment_id = None

            st.session_state.voice_input_key += 1

            st.session_state.appointment = {
                "full_name": "",
                "phone_number": "",
                "appointment_date": "",
                "appointment_time": "",
                "appointment_type": "",
                "reason": ""
            }

        elif st.session_state.awaiting_confirmation:
            if is_confirmation(user_input):
                appointment = st.session_state.appointment

                if appointment_exists(
                    appointment["appointment_date"],
                    appointment["appointment_time"]
                ):
                    add_message(
                        "assistant",
                        "That date and time are already booked. "
                        "Please select another time."
                    )

                    st.session_state.awaiting_confirmation = False
                    st.session_state.current_field = "appointment_time"
                    st.session_state.appointment["appointment_time"] = ""

                    add_message(
                        "assistant",
                        questions["appointment_time"]
                    )

                else:
                    try:
                        appointment_id = save_appointment(appointment)

                        st.session_state.appointment_id = appointment_id
                        st.session_state.booking_completed = True
                        st.session_state.awaiting_confirmation = False

                        add_message(
                            "assistant",
                            "✅ Your appointment has been confirmed "
                            f"successfully. Booking ID: {appointment_id}"
                        )

                    except Exception as error:
                        add_message(
                            "assistant",
                            "The appointment could not be saved. "
                            "Please try again."
                        )

                        print(f"Database error: {error}")

            elif is_rejection(user_input):
                add_message(
                    "assistant",
                    "Your appointment has not been booked. "
                    "You can start a new booking whenever you are ready."
                 )
                
                st.session_state.booking_started = False
                st.session_state.current_field = "full_name"
                st.session_state.awaiting_confirmation = False
                st.session_state.booking_completed = False
                st.session_state.appointment_id = None
                st.session_state.editing_field = None
                st.session_state.pending_voice_text = None
                st.session_state.voice_input_key += 1

                st.session_state.appointment = {
                    "full_name": "",
                    "phone_number": "",
                    "appointment_date": "",
                    "appointment_time": "",
                    "appointment_type": "",
                    "reason": ""
                }
 
            else:
                add_message(
                    "assistant",
                    "Please type yes to confirm or no to cancel this booking."
                )

        else:
            try:
                process_field(
                    st.session_state.current_field,
                    user_input
                )

            except Exception as error:
                add_message(
                    "assistant",
                    "Something went wrong while processing your response. "
                    "Please try again."
                )

                print(f"Application error: {error}")
        
        st.session_state.voice_input_key += 1
        st.rerun()
        


# ---------------------------------------------------
# Booking result
# ---------------------------------------------------
if st.session_state.booking_completed:
    st.success("Appointment booked successfully!")

    st.subheader("Appointment Summary")
    st.write(
    f"**Booking ID:** {st.session_state.appointment_id}"
    )

    appointment = st.session_state.appointment

    st.write(f"**Name:** {appointment['full_name']}")
    st.write(f"**Phone:** {appointment['phone_number']}")
    st.write(f"**Date:** {appointment['appointment_date']}")
    st.write(f"**Time:** {appointment['appointment_time']}")
    st.write(
        f"**Appointment Type:** "
        f"{appointment['appointment_type']}"
    )
    st.write(f"**Reason:** {appointment['reason']}")

    if st.button("Book Another Appointment"):
        reset_booking()
        st.rerun()


# ---------------------------------------------------
# Reset button
# ---------------------------------------------------
st.divider()

if st.button("Reset Application"):
    reset_booking()
    st.rerun()


