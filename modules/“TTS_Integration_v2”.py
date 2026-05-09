"""
MEGAN Auto-Generated Module: “TTS_Integration_v2”
Description: Integrates RVC cloning with the TTS.api library for testing cloned voices.
Created: 2026-05-09T12:30:40.073877
"""

python

```python
import requests
import json
import logging
from TTS.api import TTS

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class TTS_Integration:
    def __init__(self, rvc_api_url="http://localhost:8000/api/clone", tts_api_url="http://localhost:5000/tts"):
        self.rvc_api_url = rvc_api_url
        self.tts_api_url = tts_api_url
        self.tts = TTS(model_name="tts_models/en/vctk/vctk_klr", progress_bar=True, gpu=True) # Using default model

    def clone_voice(self, audio_file, target_voice):
        """Clones voice using RVC API."""
        # (Existing RVC cloning logic - same as before)
        # ... (RVC API call) ...
        pass

    def generate_speech(self, text, cloned_voice):
        """Generates speech using TTS.api."""
        try:
            # TTS.api expects a text prompt and voice name
            output = self.tts.tts(text, speaker=cloned_voice)
            audio_file = output.split(".")[0] + ".wav" # Extract filename
            logging.info(f"TTS Response: {output}")
            return audio_file
        except Exception as e:
            logging.error(f"Error during TTS API call: {e}")
            return None

    def run_full_workflow(self, audio_file, text, target_voice):
        """Orchestrates the entire process: clone voice, then generate speech."""
        cloned_audio_file = self.clone_voice(audio_file, target_voice)
        if not cloned_audio_file:
            logging.error("Voice cloning failed.")
            return None

        generated_audio_file = self.generate_speech(text, target_voice)
        if not generated_audio_file:
            logging.error("Speech generation failed.")
            return None

        logging.info(f"Full workflow complete. Cloned audio: {cloned_audio_file}, Generated speech: {generated_audio_file}")
        return generated_audio_file


# Example Usage (for testing within the module):
# tts = TTS_Integration()
# audio_file = "sample.wav"
# text = "Hello, how are you?"
# target_voice = "my_voice"
# generated_audio = tts.run_full_workflow(audio_file, text, target_voice)
# if generated_audio:
#     print(f"Generated speech saved to: {generated_audio}")
```