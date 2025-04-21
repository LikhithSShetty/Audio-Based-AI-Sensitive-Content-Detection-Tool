import whisper
import os
import logging
import json
from typing import Optional # Added for type hinting

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Transcriber:
    """
    A class to handle video transcription using OpenAI Whisper.
    """
    def __init__(self, model_name: str = "base"):
        """
        Initializes the Transcriber by loading the specified Whisper model.

        Args:
            model_name: Name of the Whisper model to use (e.g., "tiny", "base", "small").
        """
        self.model_name = model_name
        self.model = None
        try:
            logging.info(f"Loading Whisper model: {self.model_name}")
            self.model = whisper.load_model(self.model_name)
            logging.info(f"Whisper model '{self.model_name}' loaded successfully.")
        except Exception as e:
            logging.error(f"Failed to load Whisper model '{self.model_name}': {e}", exc_info=True)
            # Depending on requirements, you might want to raise the exception
            # raise e

    def transcribe_video(self, video_path: str, output_dir: str = "output") -> Optional[str]:
        """
        Transcribes the audio from a video file using the loaded Whisper model and saves the result.

        Args:
            video_path: Path to the input video file.
            output_dir: Directory to save the transcription JSON file.

        Returns:
            The file path of the saved JSON transcription, or None if transcription fails
            or the model wasn't loaded successfully.
        """
        if self.model is None:
            logging.error("Whisper model is not loaded. Cannot transcribe.")
            return None

        if not os.path.exists(video_path):
            logging.error(f"Video file not found: {video_path}")
            return None

        try:
            logging.info(f"Starting transcription for: {video_path} using model '{self.model_name}'")

            # Perform transcription with word-level timestamps
            # The transcribe function is available directly from the whisper module or the loaded model object
            result = self.model.transcribe(video_path, word_timestamps=True)

            logging.info(f"Transcription completed for: {video_path}")

            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)

            # Construct output path
            base_filename = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(output_dir, f"{base_filename}_transcription_{self.model_name}.json") # Added model name to output

            # Save the detailed result including word timestamps
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=4)

            logging.info(f"Transcription saved to: {output_path}")
            return output_path # Return the path to the saved file

        except Exception as e:
            logging.error(f"An error occurred during transcription: {e}", exc_info=True)
            return None

    # get_transcript method is removed as transcribe_video now returns the result path

# Example usage (can be run when the script is executed directly)
if __name__ == '__main__':
    # Construct path relative to the project root
    # Assumes the script is in src/transcription and the video is in the root
    script_dir = os.path.dirname(__file__)
    project_root = os.path.dirname(os.path.dirname(script_dir))
    test_video = os.path.join(project_root, "test_video.mp4")

    # --- Debugging Prints Start ---
    print(f"Script directory: {script_dir}")
    print(f"Calculated project root: {project_root}")
    print(f"Checking path: {test_video}")
    print(f"os.path.exists? {os.path.exists(test_video)}")
    print(f"os.path.isfile? {os.path.isfile(test_video)}")
    try:
        print(f"Project root contents: {os.listdir(project_root)}")
    except Exception as e:
        print(f"Error listing project root directory: {e}")
    # --- Debugging Prints End ---

    if os.path.exists(test_video):
        # Create a Transcriber instance (loads the 'tiny' model for faster testing)
        transcriber = Transcriber(model_name="tiny")

        # Check if model loaded successfully before transcribing
        if transcriber.model:
            transcription_file_path = transcriber.transcribe_video(test_video)

            if transcription_file_path:
                print(f"Transcription successful. Output saved to: {transcription_file_path}")
            else:
                print("Transcription failed.")
        else:
            print("Failed to initialize Transcriber (model loading failed).")
    else:
        print(f"Test video file not found: {test_video}. Please ensure it exists.")