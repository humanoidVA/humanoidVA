import credentials
import os
import google.generativeai as genai
from gtts import gTTS
import pygame

def main():
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

        # Get user input
        user_input = input("Ask your question: ")

        # Send user input to the model and get response
        response = chat_session.send_message(user_input)

        # Print text response
        print(response.text)

        # Convert the response text to speech using gTTS
        tts = gTTS(response.text)

        # Save the audio file
        audio_file = "response.mp3"
        tts.save(audio_file)

        # Initialize pygame mixer and play the audio file
        pygame.mixer.init()
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()

        # Keep the script alive until the audio finishes playing
        while pygame.mixer.music.get_busy():
            pass

        # Optionally, remove the audio file after playing
        os.remove(audio_file)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
