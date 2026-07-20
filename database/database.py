import sqlite3
from pathlib import Path
from typing import Any


DATABASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = DATABASE_DIR / "appointments.db"


def get_connection() -> sqlite3.Connection:
    """Create and return a SQLite database connection."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection

def normalize_phone(phone_number: str) -> str:
    """Remove spaces and common formatting characters from a phone number."""
    return (
        phone_number
        .strip()
        .replace(" ", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
    )


def initialize_database() -> None:
    """
    Create the appointments table and apply required database updates.
    """
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                phone_number TEXT NOT NULL,
                email_address TEXT,
                appointment_date TEXT NOT NULL,
                appointment_time TEXT NOT NULL,
                appointment_type TEXT NOT NULL,
                reason TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Confirmed',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Check the existing columns in the appointments table
        existing_columns = connection.execute(
            "PRAGMA table_info(appointments)"
        ).fetchall()

        existing_column_names = {
            column["name"]
            for column in existing_columns
        }

        # Add email_address to older databases without deleting records
        if "email_address" not in existing_column_names:
            connection.execute(
                """
                ALTER TABLE appointments
                ADD COLUMN email_address TEXT
                """
            )

        connection.commit()


def appointment_exists(
    appointment_date: str,
    appointment_time: str
) -> bool:
    """Check whether a confirmed appointment already uses this slot."""
    with get_connection() as connection:
        result = connection.execute(
            """
            SELECT id
            FROM appointments
            WHERE appointment_date = ?
              AND appointment_time = ?
              AND status = 'Confirmed'
            LIMIT 1
            """,
            (
                appointment_date,
                appointment_time
            )
        ).fetchone()

    return result is not None


def save_appointment(appointment: dict[str, Any]) -> int:
    """Save an appointment and return its database ID."""
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO appointments (
                full_name,
                phone_number,
                email_address,
                appointment_date,
                appointment_time,
                appointment_type,
                reason
                
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                appointment["full_name"].strip(),
                normalize_phone(appointment["phone_number"]),
                appointment.get("email_address", "").strip().lower(),
                appointment["appointment_date"],
                appointment["appointment_time"],
                appointment["appointment_type"],
                appointment["reason"].strip()
            )
        )

        connection.commit()
        appointment_id = cursor.lastrowid

    if appointment_id is None:
        raise RuntimeError("The appointment could not be saved.")

    return appointment_id


def get_all_appointments() -> list[dict[str, Any]]:
    """Return all stored appointments, ordered by date and time."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                id,
                full_name,
                phone_number,
                email_address,
                appointment_date,
                appointment_time,
                appointment_type,
                reason,
                status,
                created_at
            FROM appointments
            ORDER BY appointment_date ASC, appointment_time ASC
            """
        ).fetchall()

    return [dict(row) for row in rows]


# ---------------------------------------------------
# Appointment cancellation
# ---------------------------------------------------
def cancel_appointment(appointment_id: int) -> bool:
    """Mark a confirmed appointment as cancelled."""
    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE appointments
            SET status = 'Cancelled'
            WHERE id = ?
              AND status = 'Confirmed'
            """,
            (appointment_id,)
        )

        connection.commit()

    return cursor.rowcount > 0

# ---------------------------------------------------
# Appointment rescheduling
# ---------------------------------------------------
def reschedule_appointment(
    appointment_id: int,
    new_date: str,
    new_time: str
) -> bool:
    """Update the date and time of a confirmed appointment."""
    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE appointments
            SET appointment_date = ?,
                appointment_time = ?
            WHERE id = ?
              AND status = 'Confirmed'
            """,
            (
                new_date,
                new_time,
                appointment_id
            )
        )

        connection.commit()

    return cursor.rowcount > 0

# ---------------------------------------------------
# Find a customer's appointment
# ---------------------------------------------------
def get_verified_appointment(
    appointment_id: int,
    contact_value: str
) -> dict[str, Any] | None:
    """
    Return one appointment when the Booking ID matches
    the customer's phone number or email address.
    """
    cleaned_contact = contact_value.strip().lower()
    normalized_phone = normalize_phone(contact_value)

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                id,
                full_name,
                phone_number,
                email_address,
                appointment_date,
                appointment_time,
                appointment_type,
                reason,
                status,
                created_at
            FROM appointments
            WHERE id = ?
              AND (
                    LOWER(email_address) = ?
                    OR phone_number = ?
                  )
            LIMIT 1
            """,
            (
                appointment_id,
                cleaned_contact,
                normalized_phone
            )
        ).fetchone()

    return dict(row) if row is not None else None