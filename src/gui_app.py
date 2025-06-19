import customtkinter as ctk
from tkinter import filedialog
import os
import threading
import logging
from transcription.transcribe import Transcriber
from identification.identify import SensitiveContentIdentifier # Correct class name

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SensitiveContentApp(ctk.CTk):
    # ... __init__, select_video, update_status, display_results remain the same ...
    def __init__(self):
        super().__init__()

        self.title("Sensitive Content Detector")
        self.geometry("800x650") # Increased height for new widget

        # --- Configuration ---
        self.video_path = None
        self.transcriber = None # Initialize later
        self.identifier = SensitiveContentIdentifier() # Initialize identifier
        self.whisper_models = ["tiny", "base", "small", "medium", "large"]
        self.selected_model_name = ctk.StringVar(value="base") # Default model

        # --- Widgets ---
        # Video Selection
        self.select_video_button = ctk.CTkButton(self, text="Select Video", command=self.select_video)
        self.select_video_button.pack(pady=10)

        self.video_path_label = ctk.CTkLabel(self, text="No video selected")
        self.video_path_label.pack(pady=5)

        # Sensitive Words Input
        self.sensitive_words_label = ctk.CTkLabel(self, text="Enter sensitive words/phrases (comma-separated):")
        self.sensitive_words_label.pack(pady=5)
        self.sensitive_words_entry = ctk.CTkEntry(self, width=400)
        self.sensitive_words_entry.pack(pady=5)
        # Add a default example
        self.sensitive_words_entry.insert(0, "Alain's, capsule, data")


        # Whisper Model Selection
        self.model_select_label = ctk.CTkLabel(self, text="Select Whisper Model:")
        self.model_select_label.pack(pady=(10,0))
        self.model_select_menu = ctk.CTkOptionMenu(self, variable=self.selected_model_name, values=self.whisper_models)
        self.model_select_menu.pack(pady=5)

        # Detect Button
        self.detect_button = ctk.CTkButton(self, text="Detect Sensitive Content", command=self.start_detection_thread, state="disabled")
        self.detect_button.pack(pady=20)

        # Results Display
        self.results_label = ctk.CTkLabel(self, text="Detected Segments:")
        self.results_label.pack(pady=5)
        self.results_textbox = ctk.CTkTextbox(self, width=750, height=300, state="disabled")
        self.results_textbox.pack(pady=10, padx=10, fill="both", expand=True)

        # Status Label
        self.status_label = ctk.CTkLabel(self, text="Status: Ready")
        self.status_label.pack(pady=5, side="bottom", fill="x")

    def select_video(self):
        """Opens a file dialog to select a video file."""
        filetypes = (("Video files", "*.mp4 *.avi *.mov *.mkv"), ("All files", "*.*"))
        filepath = filedialog.askopenfilename(title="Select a Video File", filetypes=filetypes)
        if filepath:
            self.video_path = filepath
            self.video_path_label.configure(text=os.path.basename(filepath))
            self.detect_button.configure(state="normal") # Enable detect button
            logging.info(f"Video selected: {self.video_path}")
        else:
            self.video_path = None
            self.video_path_label.configure(text="No video selected")
            self.detect_button.configure(state="disabled")
            logging.info("Video selection cancelled.")

    def update_status(self, message):
        """Updates the status label (thread-safe)."""
        self.status_label.configure(text=f"Status: {message}")

    def display_results(self, results_text):
        """Displays results in the textbox (thread-safe)."""
        self.results_textbox.configure(state="normal")
        self.results_textbox.delete("1.0", ctk.END)
        self.results_textbox.insert(ctk.END, results_text)
        self.results_textbox.configure(state="disabled")

    def start_detection_thread(self):
        """Starts the detection process in a separate thread."""
        if not self.video_path:
            self.update_status("Error: No video selected.")
            return

        sensitive_input = self.sensitive_words_entry.get()
        if not sensitive_input:
            self.update_status("Error: Please enter sensitive words/phrases.")
            return

        # Disable button during processing
        self.detect_button.configure(state="disabled")
        self.select_video_button.configure(state="disabled")
        self.update_status("Processing...")
        self.display_results("") # Clear previous results

        # Run detection in a separate thread
        thread = threading.Thread(target=self.run_detection, args=(sensitive_input,), daemon=True)
        thread.start()


    def run_detection(self, sensitive_input):
        """Performs transcription and identification using GUI input."""
        try:
            # --- 1. Transcription ---
            self.update_status("Initializing transcriber...")
            # Get selected model name from the OptionMenu
            model_to_use = self.selected_model_name.get()
            logging.info(f"Selected Whisper model: {model_to_use}")

            # Initialize or re-initialize transcriber if model changed or not initialized
            if self.transcriber is None or self.transcriber.model_name != model_to_use:
                self.transcriber = Transcriber(model_name=model_to_use)

            if not self.transcriber.model:
                 raise Exception(f"Whisper model '{model_to_use}' failed to load.")

            self.update_status(f"Transcribing video (using {model_to_use} model)...")
            logging.info(f"Starting transcription for {self.video_path}")
            transcript_result = self.transcriber.transcribe_video(self.video_path)

            if not transcript_result:
                raise Exception("Transcription failed.")
            logging.info("Transcription successful.")
            self.update_status("Transcription complete.")

            # --- 2. Identification ---
            self.update_status("Identifying sensitive content...")
            # Parse sensitive words from GUI input string
            criteria_list = [word.strip() for word in sensitive_input.split(',') if word.strip()]
            if not criteria_list:
                # If input is empty after parsing, maybe fall back to config or show error?
                # For now, let's show an error/warning.
                logging.warning("No valid sensitive words provided in GUI input.")
                # Optionally, fall back to config keywords:
                # flagged_segments = self.identifier.identify_keywords(transcript_result)
                # logging.info("Using keywords from config file as fallback.")
                # For now, just report no criteria:
                raise ValueError("No valid sensitive words provided after parsing GUI input.")


            logging.info(f"Identifying using GUI criteria: {criteria_list}")

            # Call the modified identify_keywords method with the custom list
            flagged_segments = self.identifier.identify_keywords(transcript_result, custom_keywords=criteria_list)

            logging.info(f"Found {len(flagged_segments)} potentially sensitive segments.")
            self.update_status("Identification complete.")

            # --- 3. Display Results ---
            if flagged_segments:
                results_str = "Detected Segments (using GUI input):\n" + "="*35 + "\n"
                for i, segment in enumerate(flagged_segments):
                    text = segment.get('text', 'N/A').strip()
                    start = segment.get('start', -1.0) # Use -1.0 as default if missing
                    end = segment.get('end', -1.0)     # Use -1.0 as default if missing
                    # Format time nicely, handle potential None or non-float values
                    try:
                        time_str = f"{float(start):.2f}s - {float(end):.2f}s"
                    except (TypeError, ValueError):
                        time_str = f"{start} - {end}" # Fallback if conversion fails

                    results_str += f"{i+1}. Text: \"{text}\"\n   Time: {time_str}\n\n"
                self.display_results(results_str)
            else:
                self.display_results("No sensitive content matching the GUI criteria was found.")

            self.update_status("Detection finished.")

        except ValueError as ve:
             logging.error(f"Input Error: {ve}", exc_info=True)
             self.update_status(f"Error: {ve}")
             self.display_results(f"Input Error:\n{ve}")
        except Exception as e:
            logging.error(f"An error occurred during detection: {e}", exc_info=True)
            self.update_status(f"Error: {e}")
            self.display_results(f"An error occurred:\n{e}")
        finally:
            # Re-enable buttons
            self.detect_button.configure(state="normal")
            self.select_video_button.configure(state="normal")


if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    app = SensitiveContentApp()
    app.mainloop()