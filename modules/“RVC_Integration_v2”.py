"""
MEGAN Auto-Generated Module: “RVC_Integration_v2”
Description: Improved RVC integration module with enhanced error handling, logging, and JSON response parsing.
Created: 2026-05-09T12:05:45.881909
"""

python
```python
import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class RVC_Integration:
    def __init__(self, api_url="http://localhost:8000/api/clone"):
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

                try:
                    response_data = response.json()
                    logging.debug(f"RVC API Response: {response_data}") # Log the raw response

                    if 'cloned_file' in response_data:
                        cloned_file = response_data['cloned_file']
                        logging.info(f"Voice cloned successfully. Cloned file: {cloned_file}")
                        return cloned_file
                    else:
                        logging.warning(f"Error: 'cloned_file' not found in response: {response_data}")
                        return None
                except json.JSONDecodeError as e:
                    logging.error(f"Error decoding JSON response: {e}. Response text: {response.text}")
                    return None

        except requests.exceptions.RequestException as e:
            logging.error(f"Error during RVC API call: {e}")
            return None


# Example Usage (for testing within the module):
# rvc = RVC_Integration()
# cloned_audio = rvc.clone_voice("audio.wav", "my_voice")
# if cloned_audio:
#     print(f"Cloned audio saved to: {cloned_audio}")
```