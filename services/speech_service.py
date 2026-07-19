import speech_recognition as sr


def transcribe_audio(audio_file) -> tuple[bool, str]:
    """Convert a WAV audio recording into text."""
    recognizer = sr.Recognizer()

    try:
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)

        recognized_text = recognizer.recognize_google(
            audio_data,
            language="en-US"
        )

        if not recognized_text.strip():
            return False, "No speech was detected."

        return True, recognized_text.strip()

    except sr.UnknownValueError:
        return False, (
            "I could not understand the recording. "
            "Please speak clearly and try again."
        )

    except sr.RequestError:
        return False, (
            "The speech recognition service is currently unavailable. "
            "Please check your internet connection or use text input."
        )

    except Exception as error:
        print(f"Speech recognition error: {error}")

        return False, (
            "Something went wrong while processing the audio."
        )