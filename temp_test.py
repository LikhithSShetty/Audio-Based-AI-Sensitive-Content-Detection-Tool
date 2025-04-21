import json
import logging
import yaml # Need to install PyYAML: pip install PyYAML
from typing import List, Dict, Any, Optional
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SensitiveContentIdentifier:
    # ... (constructor and _load_criteria remain the same) ...
    """
    Identifies sensitive content segments in a transcription based on configured criteria.
    """
    def __init__(self, config_path: str = "config/sensitive_criteria.yaml"):
        """
        Initializes the identifier by loading criteria from the config file.

        Args:
            config_path: Path to the YAML configuration file.
        """
        # Construct absolute path for config relative to this script's location
        script_dir = os.path.dirname(__file__)
        project_root = os.path.dirname(os.path.dirname(script_dir))
        # Use the provided config_path directly if it's absolute, otherwise join with project_root
        if not os.path.isabs(config_path):
             self.config_path = os.path.join(project_root, config_path)
        else:
             self.config_path = config_path
        print(f"DEBUG: Config path calculated as: {self.config_path}") # DEBUG PRINT

        self.criteria = self._load_criteria()
        self.keywords = [kw.lower() for kw in self.criteria.get('keywords', [])] # Store keywords in lowercase
        print(f"DEBUG: Loaded keywords: {self.keywords}") # DEBUG PRINT

    def _load_criteria(self) -> Dict[str, Any]:
        """Loads identification criteria from the YAML config file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                logging.info(f"Loaded sensitive content criteria from: {self.config_path}")
                return config if config else {}
        except FileNotFoundError:
            logging.error(f"Configuration file not found: {self.config_path}")
            print(f"DEBUG: Config file not found at {self.config_path}") # DEBUG PRINT
            return {}
        except yaml.YAMLError as e:
            logging.error(f"Error parsing configuration file {self.config_path}: {e}")
            print(f"DEBUG: YAML Error parsing {self.config_path}: {e}") # DEBUG PRINT
            return {}
        except Exception as e:
            logging.error(f"An unexpected error occurred loading config {self.config_path}: {e}")
            print(f"DEBUG: Unexpected error loading config {self.config_path}: {e}") # DEBUG PRINT
            return {}


    def identify_keywords(self, transcription_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identifies sensitive segments based on keyword matching.

        Args:
            transcription_data: The loaded JSON data from Whisper transcription.

        Returns:
            A list of dictionaries, each representing a sensitive segment found
            (containing 'start', 'end', 'text', 'reason').
        """
        sensitive_segments = []
        if not self.keywords:
            logging.warning("No keywords defined in the configuration.")
            return sensitive_segments
        if 'segments' not in transcription_data:
            logging.warning("Transcription data does not contain 'segments'.")
            return sensitive_segments

        logging.info(f"Identifying sensitive content using keywords: {self.keywords}")

        # Simple approach: Check each word individually
        for segment in transcription_data.get('segments', []):
            for word_info in segment.get('words', []):
                original_word = word_info.get('word', '')
                # Remove leading/trailing whitespace AND punctuation for better matching
                # Consider using regex for more robust cleaning if needed
                cleaned_word = original_word.strip(' .,?!').lower()
                print(f"DEBUG: Checking word: '{original_word}' -> '{cleaned_word}'") # DEBUG PRINT

                # Basic check if the cleaned word itself is a keyword
                if cleaned_word in self.keywords:
                    print(f"DEBUG: Match found! Keyword: '{cleaned_word}'") # DEBUG PRINT
                    sensitive_segments.append({
                        "start": word_info.get('start'),
                        "end": word_info.get('end'),
                        "text": word_info.get('word'), # Original casing
                        "reason": f"Keyword match: '{cleaned_word}'"
                    })
                    logging.debug(f"Keyword match found: '{cleaned_word}' at {word_info.get('start')}-{word_info.get('end')}")

                # Placeholder for multi-word phrase logic
                # ...

        # TODO: Implement logic for multi-word keyword phrases

        logging.info(f"Found {len(sensitive_segments)} potential sensitive segments based on keywords.")
        print(f"DEBUG: Returning segments from identify_keywords: {sensitive_segments}") # DEBUG PRINT
        return sensitive_segments

    def identify(self, transcription_path: str) -> Optional[List[Dict[str, Any]]]:
        """
        Loads transcription and runs all identification methods.

        Args:
            transcription_path: Path to the transcription JSON file.

        Returns:
            A list of identified sensitive segments, or None if loading fails.
        """
        print(f"DEBUG: Starting identification for: {transcription_path}") # DEBUG PRINT
        try:
            # Ensure transcription_path is absolute or correctly relative to CWD
            if not os.path.isabs(transcription_path):
                 script_dir = os.path.dirname(__file__)
                 project_root = os.path.dirname(os.path.dirname(script_dir))
                 transcription_path = os.path.join(project_root, transcription_path)
                 print(f"DEBUG: Resolved relative transcription path to: {transcription_path}") # DEBUG PRINT

            with open(transcription_path, 'r', encoding='utf-8') as f:
                transcription_data = json.load(f)
            print("DEBUG: Transcription file loaded successfully.") # DEBUG PRINT
        except FileNotFoundError:
            logging.error(f"Transcription file not found: {transcription_path}")
            print(f"DEBUG: Transcription file not found at {transcription_path}.") # DEBUG PRINT
            return None
        except json.JSONDecodeError:
            logging.error(f"Error decoding JSON from file: {transcription_path}")
            print("DEBUG: JSON decode error.") # DEBUG PRINT
            return None
        except Exception as e:
            logging.error(f"An unexpected error occurred loading transcription {transcription_path}: {e}")
            print(f"DEBUG: Error loading transcription: {e}") # DEBUG PRINT
            return None

        all_sensitive_segments = []

        # --- Keyword Identification ---
        keyword_segments = self.identify_keywords(transcription_data)
        all_sensitive_segments.extend(keyword_segments)

        # --- Placeholder for NER Identification ---
        # ...

        # --- Placeholder for Semantic Identification ---
        # ...

        print(f"DEBUG: Final segments identified: {all_sensitive_segments}") # DEBUG PRINT
        return all_sensitive_segments


# Example usage
if __name__ == '__main__':
    # Construct paths relative to the project root
    script_dir = os.path.dirname(__file__)
    project_root = os.path.dirname(os.path.dirname(script_dir))
    default_config_path = os.path.join(project_root, "config/sensitive_criteria.yaml")
    default_transcription_path = os.path.join(project_root, "output/test_video_transcription_tiny.json")

    print(f"DEBUG: Running in __main__ block.") # DEBUG PRINT
    print(f"DEBUG: Using config file: {default_config_path}") # DEBUG PRINT
    print(f"DEBUG: Using transcription file: {default_transcription_path}") # DEBUG PRINT

    # Pass the absolute config path to the constructor
    identifier = SensitiveContentIdentifier(config_path=default_config_path)

    if identifier.criteria: # Check if config loaded
        print("DEBUG: Criteria loaded, proceeding with identification.") # DEBUG PRINT
        # Pass the absolute transcription path to the identify method
        identified_segments = identifier.identify(transcription_path=default_transcription_path)

        if identified_segments is not None:
            print(f"\n--- Identified Sensitive Segments ({len(identified_segments)}) ---")
            if identified_segments:
                for segment in identified_segments:
                    print(f"- Start: {segment['start']:.3f}, End: {segment['end']:.3f}, Reason: {segment['reason']}, Text: '{segment['text']}'")
            else:
                print("No sensitive segments identified.")
        else:
            print("Identification process failed (e.g., couldn't load transcription).")
    else:
        print("Identification failed: Could not load criteria from config.")
    print("DEBUG: Script finished.") # DEBUG PRINT