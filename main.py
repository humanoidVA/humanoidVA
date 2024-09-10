import credentials
import os
import google.generativeai as genai
from gtts import gTTS
import pygame
import speech_recognition as sr
import re

def main():
    recognizer = sr.Recognizer()

    try:
        # Configure API key
        genai.configure(api_key=credentials.api_key)

        # Define generation configuration for the model
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 64,
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

        print("Adjusting for ambient noise...")
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)

        while True:
            try:
                with sr.Microphone() as source:
                    print("Listening...")
                    # Set timeout and phrase_time_limit for faster response
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)

                # Recognize speech using Google's speech recognition
                try:
                    user_input = recognizer.recognize_google(audio)
                    print(f"You said: {user_input}")

                    # Check if the user said "shut down" to exit the program
                    if "shut down" in user_input.lower():
                        print("Shutting down...")
                        break

                    response_length = 40

                    # Send user input to the model and get response
                    response = chat_session.send_message(user_input + f" less than {response_length} words")

                    # Clean up the response text by removing asterisks and other unwanted symbols
                    cleaned_text = re.sub(r'[*]', '', response.text)

                    # Print cleaned text response
                    print(cleaned_text)

                    # Convert the cleaned response text to speech using gTTS
                    tts = gTTS(cleaned_text)

                    # Save the audio file
                    audio_file = "response.mp3"
                    tts.save(audio_file)

                    # Play the audio file
                    pygame.mixer.music.load(audio_file)
                    pygame.mixer.music.play()

                    # Keep the script alive until the audio finishes playing
                    while pygame.mixer.music.get_busy():
                        pass

                    # Optionally, remove the audio file after playing
                    os.remove(audio_file)

                except sr.UnknownValueError:
                    print("Google Speech Recognition could not understand the audio")
                except sr.RequestError as e:
                    print(f"Could not request results from Google Speech Recognition service; {e}")

            except KeyboardInterrupt:
                print("Exiting...")
                break

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
