import credentials
import os
import google.generativeai as genai
import pygame
import speech_recognition as sr
import re
import requests  # Import requests for manual ElevenLabs API calls
import tempfile  # Import for temporary file handling

# Set up ElevenLabs API Key
ELEVENLABS_API_KEY = credentials.elevenlabs_api_key  # Replace with your key

# Set the API key for ElevenLabs
def set_api_key(api_key):
    global ELEVENLABS_API_KEY
    ELEVENLABS_API_KEY = api_key

set_api_key(ELEVENLABS_API_KEY)

def generate_voice_response(text, voice="onwK4e9ZLuTAKqWW03F9"):
    """
    Generate a voice response using ElevenLabs REST API.
    :param text: The text to be converted into speech.
    :param voice: The name of the ElevenLabs voice model (e.g., Adam's model).
    """
    try:
        # ElevenLabs API endpoint
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}"
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
        }
        payload = {
            "text": text,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
            },
        }

        # Send POST request to ElevenLabs API
        response = requests.post(url, json=payload, headers=headers)

        # Check for successful response
        if response.status_code == 200:
            # Save audio content temporarily and play it
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
                temp_audio.write(response.content)
                audio_file = temp_audio.name

            # Play the audio using pygame
            pygame.mixer.init()
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pass

            # Clean up temporary audio file
            os.remove(audio_file)
        else:
            raise Exception(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Error generating voice response: {e}")

def introduce():
    """Introduce the assistant at the start."""
    intro_text = "Namaste! I am Jarvis, an AI assistant. How can I help you today?"
    print(intro_text)
    generate_voice_response(intro_text, voice="onwK4e9ZLuTAKqWW03F9")  # Adam's voice ID

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
        response_length = 40  # Limit response to 40 words
        response = chat_session.send_message(user_input + f" less than {response_length} words")
        cleaned_text = re.sub(r'[*]', '', response.text)  # Remove unwanted characters if any
        return cleaned_text
    except Exception as e:
        print(f"Error generating AI response: {e}")
        return "I'm sorry, I couldn't process your question right now."

def main():
    recognizer = sr.Recognizer()
    faq_file = "/home/humanoid/Desktop/humanoidVA-main/ICTMela.txt"
    faq_data = load_faq(faq_file)

    try:
        # Configure API key
        genai.configure(api_key=credentials.api_key)  # Use your existing credentials

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
                        print(f"Response: {answer}")

                    # Speak the response
                    generate_voice_response(answer, voice="onwK4e9ZLuTAKqWW03F9")  # Adam's voice ID

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
