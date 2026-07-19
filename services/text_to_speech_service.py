import pyttsx3


def speak_text(
    text: str,
    rate: int = 165,
    volume: float = 1.0
) -> tuple[bool, str]:
    """Speak the provided text using the computer's installed voice."""

    if not text or not text.strip():
        return False, "There is no text to speak."

    try:
        engine = pyttsx3.init()

        engine.setProperty("rate", rate)
        engine.setProperty("volume", volume)

        voices = engine.getProperty("voices")

        if voices:
            # Use the first installed system voice.
            engine.setProperty("voice", voices[0].id)

        engine.say(text)
        engine.runAndWait()
        engine.stop()

        return True, "Voice response completed."

    except Exception as error:
        print(f"Text-to-speech error: {error}")

        return False, (
            "The voice response could not be played. "
            "Please read the text response instead."
        )