import whisper
import os
import logging
import json
from typing import Optional, Dict, Any
import torch # Keep torch for device check

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Transcriber:
    """
    A class to handle video transcription using the Whisper model, defaulting to English.
    """
    def __init__(self, model_name: str = "base"): # Default to 'base' model here too
        """
        Initializes the Transcriber by loading the specified Whisper model.

        Args:
            model_name: Name of the Whisper model to use ("tiny", "base", "small", "medium", "large").
        """
        self.model_name = model_name
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logging.info(f"Using device: {self.device}")

        try:
            logging.info(f"Loading Whisper model: {self.model_name}")
            # Load the specified model
            self.model = whisper.load_model(self.model_name, device=self.device)
            logging.info(f"Whisper model '{self.model_name}' loaded successfully.")
        except Exception as e:
            logging.error(f"Failed to load Whisper model '{self.model_name}': {e}", exc_info=True)
            # raise e # Optional: re-raise exception to halt execution

    def transcribe_video(self, video_path: str) -> Optional[Dict[str, Any]]:
        """
        Transcribes the audio from a video file using the loaded Whisper model,
        forcing the language to English.

        Args:
            video_path: Path to the input video file.

        Returns:
            A dictionary containing the transcription result (including text, segments, words),
            or None if transcription fails or the model wasn't loaded.
        """
        if self.model is None:
            logging.error(f"Whisper model '{self.model_name}' is not loaded. Cannot transcribe.")
            return None

        if not os.path.exists(video_path):
            logging.error(f"Video file not found: {video_path}")
            return None

        try:
            logging.info(f"Starting Whisper transcription for: {video_path} (Forcing Language: English, Model: {self.model_name})")

            # Define arguments for the transcribe call
            transcribe_args = {
                "word_timestamps": True,
                "language": "en"  # Force English language
            }

            # Add FP16=False if on CPU
            if self.device == "cpu":
                transcribe_args["fp16"] = False
                logging.info("Running Whisper transcription on CPU (FP32).")

            # Call transcribe with forced English
            result = self.model.transcribe(video_path, **transcribe_args)

            logging.info(f"Whisper transcription completed for: {video_path}")
            return result # Return the dictionary directly

        except Exception as e:
            logging.error(f"An error occurred during Whisper transcription: {e}", exc_info=True)
            return None

    def save_transcription(self, transcription_result: Dict[str, Any], video_path: str, output_dir: str = "output") -> Optional[str]:
        """
        Saves the transcription result dictionary to a JSON file.

        Args:
            transcription_result: The dictionary returned by transcribe_video.
            video_path: Path to the original video file (used for naming).
            output_dir: Directory to save the transcription JSON file.

        Returns:
            The file path of the saved JSON transcription, or None if saving fails.
        """
        try:
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)

            # Construct output path including model name and language hint
            base_filename = os.path.splitext(os.path.basename(video_path))[0]
            output_filename = f"{base_filename}_transcription_whisper_{self.model_name}_en.json" # Added _en
            output_path = os.path.join(output_dir, output_filename)

            # Save the result
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(transcription_result, f, ensure_ascii=False, indent=4)

            logging.info(f"Transcription saved to: {output_path}")
            return output_path

        except Exception as e:
            logging.error(f"Failed to save transcription to JSON: {e}", exc_info=True)
            return None


# Example usage (can be run when the script is executed directly)
if __name__ == '__main__':
    # --- Configuration ---
    # Use 'base' model for better accuracy and language handling
    MODEL_NAME = "base" # <-- Use 'base' model instead of 'tiny'

    # --- File Paths ---
    script_dir = os.path.dirname(__file__)
    project_root = os.path.dirname(os.path.dirname(script_dir))
    # Ensure this is the video you want to test
    test_video_filename = "test_video6.mp4"
    test_video_path = os.path.join(project_root, test_video_filename)
    output_directory = os.path.join(project_root, "output") # Define output directory

    # --- Run Transcription ---
    if os.path.exists(test_video_path):
        # Create a Transcriber instance using the specified model
        transcriber = Transcriber(model_name=MODEL_NAME)

        # Check if model loaded successfully before transcribing
        if transcriber.model:
            logging.info(f"--- Starting WHISPER Transcription (Forcing English, Model: {MODEL_NAME}) ---")
            # Call transcribe_video (it forces English internally)
            transcript_dict = transcriber.transcribe_video(test_video_path)

            if transcript_dict:
                print("Transcription successful.")
                # Save the transcription
                saved_path = transcriber.save_transcription(transcript_dict, test_video_path, output_directory)
                if saved_path:
                    print(f"Transcription saved to: {saved_path}")
                else:
                    print("Failed to save transcription.")
            else:
                print("Transcription failed.")
        else:
            print(f"Failed to initialize Transcriber (model loading failed).")
    else:
        print(f"Test video file not found: {test_video_path}. Please ensure it exists.")