import speech_recognition as sr

def detect_background_voice():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source, timeout=3)
    try:
        r.recognize_google(audio)
        return Tru
    except:
        return False
