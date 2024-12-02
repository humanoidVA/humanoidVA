import espeakng

def text_to_speech_espeak(text):
    espeak = espeakng.ESpeakNG()
    espeak.voice = 'en+m2'    # Try different voices: 'en+m1', 'en+m2', etc.
    espeak.pitch = 40         # Lower pitch for natural tone
    espeak.speed = 130        # Slow down for better clarity
    espeak.say(text)

def introduce():
    intro_text = "Namaste! I am Jarvis, an AI assistant. How can I help you today?"
    print(intro_text)
    text_to_speech_espeak(intro_text)

if __name__ == "__main__":
    introduce()
