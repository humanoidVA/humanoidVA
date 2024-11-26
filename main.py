import credentials
import os
import google.generativeai as genai
from gtts import gTTS
import pygame
import speech_recognition as sr
import re

def introduce():
    """Introduce the assistant at the start."""
    intro_text = "Hello! I am Jarvis, an AI assistant. How can I help you today?"
    print(intro_text)
    tts = gTTS(intro_text)
    audio_file = "intro.mp3"
    tts.save(audio_file)
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pass
    os.remove(audio_file)

def load_faq(file_path):
    """Load FAQ data from a text file into a dictionary."""
    faq = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            current_question = None
            for line in file:
                line = line.strip()
                if line.endswith("?"):
                    current_question = line
                    faq[current_question] = ""
                elif current_question:
                    faq[current_question] += line + " "
        return faq
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return {}

def answer_faq(user_input, faq):
    """Check if the question is in the FAQ and return the answer."""
    for question, answer in faq.items():
        if user_input.lower() in question.lower():
            return answer.strip()
    return None

def generate_ai_response(chat_session, user_input):
    """Generate a response using the AI model."""
    try:
        response_length = 40
        response = chat_session.send_message(user_input + f" less than {response_length} words")
        cleaned_text = re.sub(r'[*]', '', response.text)
        return cleaned_text
    except Exception as e:
        print(f"Error generating AI response: {e}")
        return "I'm sorry, I couldn't process your question right now."

def main():
    recognizer = sr.Recognizer()
    faq_file = "ICTMela.txt"
    faq_data = load_faq(faq_file)

    try:
        # Configure API key
        genai.configure(api_key=credentials.api_key)  # Retained your original API key configuration

        # Define generation configuration for the model
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }

        # Create and configure the model
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
        )

        # Start a chat session
        chat_session = model.start_chat(history=[])

        # Initialize pygame mixer
        pygame.mixer.init()

        # Introduce the assistant
        introduce()

        print("Adjusting for ambient noise...")
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)

        while True:
            try:
                with sr.Microphone() as source:
                    print("Listening...")
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)

                try:
                    user_input = recognizer.recognize_google(audio)
                    print(f"You said: {user_input}")

                    # Check for shutdown command
                    if "shut down" in user_input.lower():
                        print("Shutting down...")
                        break

                    # Check if the input matches any FAQ question
                    answer = answer_faq(user_input, faq_data)

                    if answer:
                        print(f"FAQ Answer: {answer}")
                    else:
                        print("Generating AI response...")
                        answer = generate_ai_response(chat_session, user_input)

                    tts = gTTS(answer)
                    audio_file = "response.mp3"
                    tts.save(audio_file)

                    pygame.mixer.music.load(audio_file)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        pass
                    os.remove(audio_file)

                except sr.UnknownValueError:
                    print("Sorry, I could not understand the audio. Please try again.")
                except sr.RequestError as e:
                    print(f"Could not request results from Google Speech Recognition service; {e}")
                except sr.WaitTimeoutError:
                    print("Listening timed out. Please speak louder or clearer.")

            except sr.WaitTimeoutError:
                print("Timeout waiting for input, continuing to listen...")

            except KeyboardInterrupt:
                print("Exiting...")
                break

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
