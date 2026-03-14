import customtkinter as ctk
from tkinter import filedialog
import threading

from vocab_audio_automator.utils.constants import GUIStrings
from vocab_audio_automator.core.core import run_pipeline


class GeneratorTab(ctk.CTkFrame):
    def __init__(self, parent, app_controller, **kwargs):
        """
        parent: The parent element (e.g. CTkTabview)
        app_controller: reference to the main app
        """
        super().__init__(parent, **kwargs)
        self.output_dir = "outputs"

        self.app_controller = app_controller
        self.selected_file_path = None
        self._create_widgets()
        
    def _create_widgets(self):
        """Creates all visiual elements of the tab"""
        self.title_label = ctk.CTkLabel(
            self,
            text=GUIStrings.LABEL_GENERATOR_TAB_TITLE,
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        self.title_label.pack(pady=(10, 5))

        self.switch_audio_only = ctk.CTkSwitch(
            self,
            text=GUIStrings.LABEL_AUDIO_ONLY_TOGGLE_TITLE,
            command=self._toggle_mode,
        )
        self.switch_audio_only.pack(pady=(0, 15))

        self.btn_select_file = ctk.CTkButton(
            self, text=GUIStrings.BUTTON_CSV, command=self._select_file
        )
        self.btn_select_file.pack(pady=5)

        self.lbl_file = ctk.CTkLabel(
            self, text=GUIStrings.LABEL_NO_FILE_SELECTED, text_color="gray"
        )
        self.lbl_file.pack(pady=(0, 5))

        self.btn_select_output = ctk.CTkButton(
            self,
            text=GUIStrings.BUTTON_OUTPUT,
            command=self._select_output_dir,
            fg_color="gray",
        )
        self.btn_select_output.pack(pady=5)
        self.lbl_output = ctk.CTkLabel(
            self,
            text=GUIStrings.LABEL_OUTPUT_DIRECTORY.format(dir=self.output_dir),
            text_color="gray",
        )
        self.lbl_output.pack(pady=(0, 5))

        self.lbl_deck_desc = ctk.CTkLabel(
            self,
            text=GUIStrings.LABEL_ANKI_DECK_NAME,
            font=ctk.CTkFont(weight="bold"),
        )
        self.lbl_deck_desc.pack(pady=(10, 0))
        self.entry_deck_name = ctk.CTkEntry(
            self, placeholder_text=GUIStrings.PLACEHOLDER_DECK_NAME, width=300
        )
        self.entry_deck_name.pack(pady=(5, 5))

        self.lbl_filename_desc = ctk.CTkLabel(
            self,
            text=GUIStrings.LABEL_OUTPUT_NAME,
            font=ctk.CTkFont(weight="bold"),
        )
        self.lbl_filename_desc.pack(pady=(5, 0))
        self.entry_filename = ctk.CTkEntry(
            self, placeholder_text=GUIStrings.PLACEHOLDER_FILE_NAME, width=300
        )
        self.entry_filename.pack(pady=(5, 10))

        self.btn_generate = ctk.CTkButton(
            self,
            text=GUIStrings.BUTTON_START_GENERATION,
            command=self._start_generation,
            height=40,
        )
        self.btn_generate.pack(pady=(15, 10))

        self.progress_bar = ctk.CTkProgressBar(self, width=400)
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(self, text="")
        self.status_label.pack(pady=10)

    # ==========================================
    # EVENT HANDLERS (Was passiert bei Klicks?)
    # ==========================================

    def _toggle_mode(self):
        """Changes the UI based on whether Audio-Only mode is enabled."""
        if self.switch_audio_only.get():
            self.btn_select_file.configure(text=GUIStrings.BUTTON_TXT)
            self.file_types = [("Text Files", "*.txt")]
            self.lbl_file.configure(
                text=GUIStrings.LABEL_FORMAT_REQUIRED, text_color="yellow"
            )
        else:
            self.btn_select_file.configure(text=GUIStrings.BUTTON_CSV)
            self.file_types = [("CSV Files", "*.csv")]
            self.lbl_file.configure(
                text=GUIStrings.LABEL_NO_FILE_SELECTED, text_color="gray"
            )

        self.input_path = None

    def _select_file(self):
        """Called when the select file button is pressed"""
        filename = filedialog.askopenfilename(filetypes=self.file_types)
        if filename:
            self.input_path = filename
            self.lbl_file.configure(text=filename.split("/")[-1], text_color="white")

    def _select_output_dir(self):
        """
        Opens a file dialog to select an output directory and updates the UI.

        This event handler prompts the user to select a directory. If a valid
        directory is chosen, it stores the path in the instance and updates the
        output label on the GUI. To prevent UI distortion, the displayed path
        is truncated with an ellipsis (...) if it exceeds 40 characters.

        Side Effects:
            self.output_dir (str): Updated with the selected directory path.
            self.lbl_output (Widget): The text is updated with the formatted
                path and the text color is set to white.
        """
        dirname = filedialog.askdirectory(title=GUIStrings.BUTTON_OUTPUT)
        if dirname:
            self.output_dir = dirname
            display_path = dirname if len(dirname) < 40 else "..." + dirname[-37:]
            self.lbl_output.configure(
                text=GUIStrings.LABEL_OUTPUT_DIRECTORY.format(dir=display_path),
                text_color="white",
            )

    def _start_generation(self):
        """
        Validates user inputs and starts the generation process in a background thread.

        This method performs a series of pre-flight checks before executing the main
        generation logic. It verifies that an input file is selected, checks the file
        extension based on the selected mode (Audio Only vs. Standard), and performs
        a quick peek into the file to ensure the required formatting is present
        (a pipe `|` character for TXT files, or a 'word' header for CSV files).

        If all validations pass, the UI is locked to prevent duplicate submissions,
        and the actual generation task (`run_worker`) is handed off to a daemon thread
        to keep the GUI responsive.

        Side Effects:
            Updates the GUI status label via `self.update_status` if errors occur.
            Disables `self.btn_generate` and `self.switch_audio_only` to prevent
                concurrent runs.
            Displays and resets `self.progress_bar`.
            Spawns a new daemon thread targeting the `self.run_worker` method.
        """
        if not self.input_path:
            self._update_status(GUIStrings.LABEL_ERROR_SELECT_FILE, "red")
            return

        is_audio_only = self.switch_audio_only.get()

        if is_audio_only and not self.input_path.lower().endswith(".txt"):
            self._update_status(GUIStrings.LABEL_ERROR_TXT_FILE, "red")
            return
        elif not is_audio_only and not self.input_path.lower().endswith(".csv"):
            self._update_status(GUIStrings.LABEL_ERROR_CSV_FILE, "red")
            return

        try:
            if is_audio_only:
                valid_format = False
                with open(self.input_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip() and "|" in line:
                            valid_format = True
                            break
                if not valid_format:
                    self._update_status(GUIStrings.LABEL_ERROR_INVALID_TXT, "red")
                    return
            else:
                import csv

                with open(self.input_path, "r", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    headers = next(reader, [])
                    headers_clean = [h.strip().lower() for h in headers]
                    if "word" not in headers_clean:
                        self._update_status(
                            GUIStrings.LABEL_ERROR_WORD_COLUMN,
                            "red",
                        )
                        return
        except Exception as e:
            self._update_status(GUIStrings.LABEL_GENERAL_ERROR.format(exc=e), "red")
            return

        if not self.entry_deck_name.get().strip():
            self._update_status(GUIStrings.LABEL_ERROR_ANKI_NAME, "red")
            return
        if not self.entry_filename.get().strip():
            self._update_status(GUIStrings.LABEL_ERROR_OUTPUT_NAME, "red")
            return

        self.btn_generate.configure(state="disabled")
        self.switch_audio_only.configure(state="disabled")
        self.progress_bar.pack(pady=5)
        self.progress_bar.set(0)
        self._update_status("Starting...", "yellow")
        threading.Thread(target=self._run_worker, daemon=True).start()

    def _update_status(self, message, color="white"):
        self.after(
            0, lambda: self.status_label.configure(text=message, text_color=color)
        )

    def _update_progress(self, value):
        self.after(0, lambda: self.progress_bar.set(value))

    def _run_worker(self):
        """
        Executes the main processing pipeline, typically run in a background thread.
        
        Retrieves user input from the GUI components, passes them into the 
        main `run_pipeline` function, and handles the success state. It uses 
        thread-safe callbacks to update the GUI's progress and status during 
        execution. Finally, it ensures the GUI controls are re-enabled on the 
        main thread once the process finishes.

        Side Effects:
            - Reads states from `self.entry_filename`, `self.entry_deck_name`, 
              and `self.switch_audio_only`.
            - Calls `self.update_status` and `self.update_progress`.
            - Schedules GUI updates using `self.after` to re-enable 
              `self.btn_generate` and `self.switch_audio_only`.
        """
        custom_name = self.entry_filename.get().strip()
        target_deck = self.entry_deck_name.get().strip()
        audio_only_mode = self.switch_audio_only.get()

        success = run_pipeline(
            self.input_path,
            output_dir=self.output_dir,
            output_name=custom_name,
            target_deck_name=target_deck,
            run_audio_only=audio_only_mode,
            status_callback=self.update_status,
            progress_callback=self.update_progress,
        )
        if success:
            self.update_status(
                GUIStrings.LABEL_GENERATION_SUCCESS.format(file=custom_name), "green"
            )
            self.update_progress(1.0)

        self.after(0, lambda: self.btn_generate.configure(state="normal"))
        self.after(0, lambda: self.switch_audio_only.configure(state="normal"))
