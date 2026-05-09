"""
MEGAN Auto-Generated Module: “RVC_Integration”
Description: Integrates with the Realtime Voice Cloning (RVC) model for voice cloning functionality.
Created: 2026-05-07T20:02:45.382106
"""


import requests
import json

class RVC_Integration:
    def __init__(self, api_url="http://localhost:8000/api/clone"): #Assumes RVC is running locally
        self.api_url = api_url

    def clone_voice(self, audio_file, target_voice):
        """
        Clones the target voice from the audio file using the RVC API.

        Args:
            audio_file (str): Path to the audio file.
            target_voice (str): Name of the voice to clone.

        Returns:
            str: Cloned audio file path, or None if an error occurred.
        """
        try:
            with open(audio_file, 'rb') as audio_data:
                files = {'audio': audio_data}
                data = {'target_voice': target_voice}
                response = requests.post(self.api_url, files=files, data=data)
                response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
                cloned_file = response.json()['cloned_file']
                return cloned_file
        except requests.exceptions.RequestException as e:
            print(f"Error during RVC API call: {e}")
            return None

# Example Usage (for testing within the module):
# rvc = RVC_Integration()
# cloned_audio = rvc.clone_voice("audio.wav", "my_voice")
# if cloned_audio:
#     print(f"Cloned audio saved to: {cloned_audio}")