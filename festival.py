import subprocess

def text_to_speech_festival(text):
    subprocess.run(['festival', '--tts'], input=text, text=True)

def introduce():
    intro_text = "Namaste! I am Jarvis, an AI assistant. How can I help you today?"
    print(intro_text)
    text_to_speech_festival(intro_text)

if __name__ == "__main__":
    introduce()
