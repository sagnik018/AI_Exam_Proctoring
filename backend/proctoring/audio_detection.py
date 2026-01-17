import speech_recognition as sr
import time

recognizer = sr.Recognizer()
recognizer.dynamic_energy_threshold = True

# Cooldown to avoid repeated triggers
LAST_DETECTED_TIME = 0
COOLDOWN_SECONDS = 5


def detect_background_voice(timeout=1):
    """
    Detects background human speech.
    Returns True only if speech is detected and cooldown has passed.
    """

    global LAST_DETECTED_TIME

    current_time = time.time()
    if current_time - LAST_DETECTED_TIME < COOLDOWN_SECONDS:
        return False

    try:
        with sr.Microphone() as source:
            # Adjust for ambient noise (very important)
            recognizer.adjust_for_ambient_noise(source, duration=0.3)

            audio = recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=2
            )

        # If speech is recognized → background voice detected
        recognizer.recognize_google(audio)

        LAST_DETECTED_TIME = current_time
        return True

    except sr.WaitTimeoutError:
        return False
    except sr.UnknownValueError:
        # Noise but not speech
        return False
    except sr.RequestError:
        # API issue, ignore safely
        return False
    except Exception:
        return False
