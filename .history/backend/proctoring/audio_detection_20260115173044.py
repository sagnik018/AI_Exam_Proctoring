import speech_recognition as sr

recognizer = sr.Recognizer()
recognizer.energy_threshold = 3000

def detect_background_voice(timeout=1):
    try:
        with sr.Microphone() as source:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=2)
        recognizer.recognize_google(audio)
        return True
    except:
        return False
