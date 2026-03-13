import os
import sys
import yaml
import threading
import customtkinter as ctk
from tkinter import filedialog
from dotenv import load_dotenv, set_key

from vocab_audio_automator.core.core import run_pipeline
from vocab_audio_automator.utils.strings import GUIStrings

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

LLM_PROVIDER = ["openai, claude"]
AUDIO_PROVIDER = ["openai", "edge_tts"]


class AnkiGeneratorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        WINDOW_WIDTH = 700
        WINDOW_HEIGHT = 850
        self.title(GUIStrings.APP_TITLE)

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_coordinate = int((screen_width / 2) - (WINDOW_WIDTH / 2))
        y_coordinate = int((screen_height / 2) - (WINDOW_HEIGHT / 2))
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x_coordinate}+{y_coordinate}")

        self.input_path = None
        self.output_dir = "outputs"
        self.file_types = [("CSV Files", "*.csv")]  # Default format

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(padx=20, pady=10, fill="both", expand=True)

        self.tab_gen = self.tabview.add(GUIStrings.GEN_TAB_NAME)
        self.tab_set = self.tabview.add(GUIStrings.SETTINGS_TAB_NAME)
        self.tab_adv = self.tabview.add(GUIStrings.ADVANDCED_TAB_NAME)

        self.setup_generator_tab()
        self.setup_settings_tab()
        self.setup_advanced_tab()
        self.load_current_settings()

    ####################
    # TAB 1: GENERATOR #
    ####################
    def setup_generator_tab(self):
        self.title_label = ctk.CTkLabel(
            self.tab_gen,
            text=GUIStrings.LABEL_GENERATOR_TAB_TITLE,
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        self.title_label.pack(pady=(10, 5))

        self.switch_audio_only = ctk.CTkSwitch(
            self.tab_gen,
            text=GUIStrings.LABEL_AUDIO_ONLY_TOGGLE_TITLE,
            command=self.toggle_mode,
        )
        self.switch_audio_only.pack(pady=(0, 15))

        self.btn_select_file = ctk.CTkButton(
            self.tab_gen, text=GUIStrings.BUTTON_CSV, command=self.select_file
        )
        self.btn_select_file.pack(pady=5)
        self.lbl_file = ctk.CTkLabel(
            self.tab_gen, text=GUIStrings.LABEL_NO_FILE_SELECTED, text_color="gray"
        )
        self.lbl_file.pack(pady=(0, 5))

        self.btn_select_output = ctk.CTkButton(
            self.tab_gen,
            text=GUIStrings.BUTTON_OUTPUT,
            command=self.select_output_dir,
            fg_color="gray",
        )
        self.btn_select_output.pack(pady=5)
        self.lbl_output = ctk.CTkLabel(
            self.tab_gen,
            text=GUIStrings.LABEL_OUTPUT_DIRECTORY.format(dir=self.output_dir),
            text_color="gray",
        )
        self.lbl_output.pack(pady=(0, 5))

        self.lbl_deck_desc = ctk.CTkLabel(
            self.tab_gen,
            text=GUIStrings.LABEL_ANKI_DECK_NAME,
            font=ctk.CTkFont(weight="bold"),
        )
        self.lbl_deck_desc.pack(pady=(10, 0))
        self.entry_deck_name = ctk.CTkEntry(
            self.tab_gen, placeholder_text=GUIStrings.PLACEHOLDER_DECK_NAME, width=300
        )
        self.entry_deck_name.pack(pady=(5, 5))

        self.lbl_filename_desc = ctk.CTkLabel(
            self.tab_gen,
            text=GUIStrings.LABEL_OUTPUT_NAME,
            font=ctk.CTkFont(weight="bold"),
        )
        self.lbl_filename_desc.pack(pady=(5, 0))
        self.entry_filename = ctk.CTkEntry(
            self.tab_gen, placeholder_text=GUIStrings.PLACEHOLDER_FILE_NAME, width=300
        )
        self.entry_filename.pack(pady=(5, 10))

        self.btn_generate = ctk.CTkButton(
            self.tab_gen,
            text=GUIStrings.BUTTON_START_GENERATION,
            command=self.start_generation,
            height=40,
        )
        self.btn_generate.pack(pady=(15, 10))

        self.progress_bar = ctk.CTkProgressBar(self.tab_gen, width=400)
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(self.tab_gen, text="")
        self.status_label.pack(pady=10)

    ###############################################
    # TAB 2 & 3: SETTINGS                         #
    ###############################################
    def setup_settings_tab(self):
        self.scroll_frame_set = ctk.CTkScrollableFrame(
            self.tab_set, fg_color="transparent"
        )
        self.scroll_frame_set.pack(fill="both", expand=True)

        def create_labeled_entry(parent, label_text, placeholder, is_password=False):
            ctk.CTkLabel(parent, text=label_text, text_color="gray").pack(
                anchor="w", padx=10, pady=(5, 0)
            )
            entry = ctk.CTkEntry(
                parent,
                placeholder_text=placeholder,
                width=450,
                show="*" if is_password else "",
            )
            entry.pack(anchor="w", padx=10, pady=(0, 5))
            return entry

        ctk.CTkLabel(
            self.scroll_frame_set,
            text=GUIStrings.LABEL_API_KEYS_TITLE,
            font=ctk.CTkFont(weight="bold", size=16),
        ).pack(anchor="w", pady=(10, 5))
        self.entry_openai = create_labeled_entry(
            self.scroll_frame_set,
            GUIStrings.LABEL_OPENAI_KEY,
            GUIStrings.PLACEHOLDER_OPENAI_KEY,
            is_password=True,
        )
        self.entry_claude = create_labeled_entry(
            self.scroll_frame_set,
            GUIStrings.LABEL_ANTHROPIC_KEY,
            GUIStrings.PLACEHOLDER_ANTHROPIC_KEY,
            is_password=True,
        )

        ctk.CTkLabel(
            self.scroll_frame_set,
            text=GUIStrings.LABEL_LANGUAGE_DEFAULTS_TITLE,
            font=ctk.CTkFont(weight="bold", size=16),
        ).pack(anchor="w", pady=(20, 5))
        self.entry_target = create_labeled_entry(
            self.scroll_frame_set,
            GUIStrings.LABEL_TARGET_LANGUAGE,
            GUIStrings.PLACEHOLDER_TARGET_LANGUAGE,
        )
        self.entry_source = create_labeled_entry(
            self.scroll_frame_set,
            GUIStrings.LABEL_SOURCE_LANGUAGE,
            GUIStrings.PLACEHOLDER_SOURCE_LANGUAGE,
        )
        self.entry_level = create_labeled_entry(
            self.scroll_frame_set,
            GUIStrings.LABEL_LANGUAGE_LEVEL,
            GUIStrings.PLACEHOLDER_LANGUAGE_LEVEL,
        )
        self.entry_sentences = create_labeled_entry(
            self.scroll_frame_set,
            GUIStrings.LABEL_NUM_SENTENCES,
            GUIStrings.PLACEHOLDER_NUM_SENTENCES,
        )
        self.entry_setting = create_labeled_entry(
            self.scroll_frame_set,
            GUIStrings.LABEL_SETTING,
            GUIStrings.PLACEHOLDER_SETTING,
        )

        ctk.CTkLabel(
            self.scroll_frame_set,
            text=GUIStrings.LABEL_LLM_PROVIDERS_TITLE,
            font=ctk.CTkFont(weight="bold", size=16),
        ).pack(anchor="w", pady=(20, 5))
        ctk.CTkLabel(
            self.scroll_frame_set,
            text=GUIStrings.LABEL_SENTENCE_PROVIDER,
            text_color="gray",
        ).pack(anchor="w", padx=10, pady=(5, 0))
        self.opt_sentence_provider = ctk.CTkOptionMenu(
            self.scroll_frame_set, values=LLM_PROVIDER, width=450
        )
        self.opt_sentence_provider.pack(anchor="w", padx=10, pady=(0, 5))
        ctk.CTkLabel(
            self.scroll_frame_set,
            text=GUIStrings.LABEL_AUDIO_PROVIDER,
            text_color="gray",
        ).pack(anchor="w", padx=10, pady=(5, 0))
        self.opt_audio_provider = ctk.CTkOptionMenu(
            self.scroll_frame_set, values=AUDIO_PROVIDER, width=450
        )
        self.opt_audio_provider.pack(anchor="w", padx=10, pady=(0, 5))

        ctk.CTkLabel(
            self.scroll_frame_set,
            text=GUIStrings.LABEL_MODEL_DETAILS,
            font=ctk.CTkFont(weight="bold", size=16),
        ).pack(anchor="w", pady=(20, 5))
        self.entry_openai_sent_model = create_labeled_entry(
            self.scroll_frame_set,
            GUIStrings.LABEL_OPENAI_MODEL_ID,
            GUIStrings.PLACEHOLDER_OPENAI_MODEL_ID,
        )
        self.entry_openai_audio_model = create_labeled_entry(
            self.scroll_frame_set,
            GUIStrings.LABEL_OPENAI_AUDIO_ID,
            GUIStrings.PLACEHOLDER_OPENAI_AUDIO_ID,
        )
        self.entry_openai_voices = create_labeled_entry(
            self.scroll_frame_set,
            GUIStrings.LABEL_OPENAI_VOICES,
            GUIStrings.PLACEHOLDER_OPENAI_VOICES,
        )
        self.entry_claude_model = create_labeled_entry(
            self.scroll_frame_set,
            GUIStrings.LABEL_CLAUDE_MODEL_ID,
            GUIStrings.PLACEHOLDER_CLAUDE_MODEL_ID,
        )
        self.entry_edge_voices = create_labeled_entry(
            self.scroll_frame_set,
            GUIStrings.LABEL_EDGE_TTS_VOICES,
            GUIStrings.PLACEHOLDER_EDGE_TTS_VOICES,
        )

        self.btn_save_settings = ctk.CTkButton(
            self.scroll_frame_set,
            text=GUIStrings.BUTTON_SAVE_SETTINGS,
            command=self.save_settings,
            fg_color="green",
            hover_color="darkgreen",
            height=40,
        )
        self.btn_save_settings.pack(pady=(30, 20))
        self.lbl_settings_status = ctk.CTkLabel(self.scroll_frame_set, text="")
        self.lbl_settings_status.pack(pady=(0, 10))

    def setup_advanced_tab(self):
        self.scroll_frame_adv = ctk.CTkScrollableFrame(
            self.tab_adv, fg_color="transparent"
        )
        self.scroll_frame_adv.pack(fill="both", expand=True)

        def create_labeled_textbox(parent, label_text, height=100):
            ctk.CTkLabel(
                parent,
                text=label_text,
                text_color="gray",
                font=ctk.CTkFont(weight="bold"),
            ).pack(anchor="w", padx=10, pady=(15, 2))
            textbox = ctk.CTkTextbox(parent, width=550, height=height)
            textbox.pack(anchor="w", padx=10, pady=(0, 5))
            return textbox

        ctk.CTkLabel(
            self.scroll_frame_adv,
            text=GUIStrings.LABEL_ANKI_CONFIG,
            font=ctk.CTkFont(weight="bold", size=16),
        ).pack(anchor="w", pady=(10, 5))
        ctk.CTkLabel(
            self.scroll_frame_adv,
            text=GUIStrings.LABEL_ANKI_DECK_ID,
            text_color="gray",
        ).pack(anchor="w", padx=10, pady=(5, 0))
        self.entry_model_id = ctk.CTkEntry(self.scroll_frame_adv, width=300)
        self.entry_model_id.pack(anchor="w", padx=10, pady=(0, 15))

        ctk.CTkLabel(
            self.scroll_frame_adv,
            text=GUIStrings.LABEL_MAIN_PROMPT,
            font=ctk.CTkFont(weight="bold", size=16),
        ).pack(anchor="w", pady=(20, 5))
        self.tb_system_prompt = create_labeled_textbox(
            self.scroll_frame_adv, GUIStrings.LABEL_SYSTEM_PROMPT, height=80
        )
        self.tb_sentence_gen = create_labeled_textbox(
            self.scroll_frame_adv, GUIStrings.LABEL_SENTENCE_PROMPT, height=200
        )
        self.tb_audio_inst = create_labeled_textbox(
            self.scroll_frame_adv, GUIStrings.LABEL_AUDIO_INSTRUCTIONS, height=80
        )

        ctk.CTkLabel(
            self.scroll_frame_adv,
            text=GUIStrings.LABEL_MODULAR_PROMPTS,
            font=ctk.CTkFont(weight="bold", size=16),
        ).pack(anchor="w", pady=(20, 5))
        self.tb_global_words = create_labeled_textbox(
            self.scroll_frame_adv, GUIStrings.LABEL_GLOBAL_WORDS, height=60
        )
        self.tb_bonus_all = create_labeled_textbox(
            self.scroll_frame_adv, GUIStrings.LABEL_BONUS_WORDS_ALL, height=60
        )
        self.tb_bonus_some = create_labeled_textbox(
            self.scroll_frame_adv, GUIStrings.LABEL_BONUS_WORDS_SOME, height=60
        )

        self.btn_save_adv = ctk.CTkButton(
            self.scroll_frame_adv,
            text=GUIStrings.BUTTON_SAVE_ADVANCED,
            command=self.save_advanced_settings,
            fg_color="darkred",
            hover_color="#6b0000",
            height=40,
        )
        self.btn_save_adv.pack(pady=(30, 20))
        self.lbl_adv_status = ctk.CTkLabel(self.scroll_frame_adv, text="")
        self.lbl_adv_status.pack(pady=(0, 10))

    ####################
    # LOGIC: GENERATOR #
    ####################
    def toggle_mode(self):
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

        self.input_path = None  # Reset selected file when switching modes

    def select_file(self):
        filename = filedialog.askopenfilename(filetypes=self.file_types)
        if filename:
            self.input_path = filename
            self.lbl_file.configure(text=filename.split("/")[-1], text_color="white")

    def select_output_dir(self):
        dirname = filedialog.askdirectory(title=GUIStrings.BUTTON_OUTPUT)
        if dirname:
            self.output_dir = dirname
            display_path = dirname if len(dirname) < 40 else "..." + dirname[-37:]
            self.lbl_output.configure(
                text=GUIStrings.LABEL_OUTPUT_DIRECTORY.format(dir=display_path),
                text_color="white",
            )

    def start_generation(self):
        if not self.input_path:
            self.update_status(GUIStrings.LABEL_ERROR_SELECT_FILE, "red")
            return

        is_audio_only = self.switch_audio_only.get()

        if is_audio_only and not self.input_path.lower().endswith(".txt"):
            self.update_status(GUIStrings.LABEL_ERROR_TXT_FILE, "red")
            return
        elif not is_audio_only and not self.input_path.lower().endswith(".csv"):
            self.update_status(GUIStrings.LABEL_ERROR_CSV_FILE, "red")
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
                    self.update_status(GUIStrings.LABEL_ERROR_INVALID_TXT, "red")
                    return
            else:
                import csv

                with open(self.input_path, "r", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    headers = next(reader, [])
                    headers_clean = [h.strip().lower() for h in headers]
                    if "word" not in headers_clean:
                        self.update_status(
                            GUIStrings.LABEL_ERROR_WORD_COLUMN,
                            "red",
                        )
                        return
        except Exception as e:
            self.update_status(GUIStrings.LABEL_GENERAL_ERROR.format(exc=e), "red")
            return

        if not self.entry_deck_name.get().strip():
            self.update_status(GUIStrings.LABEL_ERROR_ANKI_NAME, "red")
            return
        if not self.entry_filename.get().strip():
            self.update_status(GUIStrings.LABEL_ERROR_OUTPUT_NAME, "red")
            return

        self.btn_generate.configure(state="disabled")
        self.switch_audio_only.configure(state="disabled")
        self.progress_bar.pack(pady=5)
        self.progress_bar.set(0)
        self.update_status("Starting...", "yellow")
        threading.Thread(target=self.run_worker, daemon=True).start()

    def update_status(self, message, color="white"):
        self.after(
            0, lambda: self.status_label.configure(text=message, text_color=color)
        )

    def update_progress(self, value):
        self.after(0, lambda: self.progress_bar.set(value))

    def run_worker(self):
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

    #################################
    # LOGIC: SETTINGS (Load & Save) #
    #################################
    def get_env_path(self):
        if getattr(sys, "frozen", False):
            return os.path.join(os.path.dirname(sys.executable), ".env")
        return ".env"

    def load_current_settings(self):
        env_path = self.get_env_path()
        load_dotenv(dotenv_path=env_path, override=True)
        self.entry_openai.insert(0, os.getenv("OPENAI_API_KEY", ""))
        self.entry_claude.insert(0, os.getenv("ANTHROPIC_API_KEY", ""))

        try:
            with open("config.yaml", "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}

            anki_cfg = config.get("anki", {})
            self.entry_deck_name.insert(0, anki_cfg.get("deck_name", ""))
            self.entry_model_id.insert(0, str(anki_cfg.get("model_id", "")))

            defaults = config.get("defaults", {})
            self.entry_target.insert(0, defaults.get("target_language", ""))
            self.entry_source.insert(0, defaults.get("source_language", ""))
            self.entry_level.insert(0, defaults.get("level", ""))
            self.entry_sentences.insert(0, str(defaults.get("number_of_sentences", "")))
            self.entry_setting.insert(0, defaults.get("setting", ""))

            model_config = config.get("model", {})
            self.opt_sentence_provider.set(model_config.get("sentence_generation", ""))
            self.opt_audio_provider.set(model_config.get("audio", ""))

            openai_cfg = config.get("openai", {})
            self.entry_openai_sent_model.insert(
                0, openai_cfg.get("sentence_generation", {}).get("model_id", "")
            )
            self.entry_openai_audio_model.insert(
                0, openai_cfg.get("audio", {}).get("model_id", "")
            )
            self.entry_openai_voices.insert(
                0, ", ".join(openai_cfg.get("audio", {}).get("voices", []))
            )

            claude_cfg = config.get("claude", {})
            self.entry_claude_model.insert(0, claude_cfg.get("model_id", ""))

            edge_cfg = config.get("edge_tts", {})
            self.entry_edge_voices.insert(0, ", ".join(edge_cfg.get("voices", [])))

            prompts = config.get("prompts", {})
            self.tb_system_prompt.insert("1.0", prompts.get("system_prompt", ""))
            self.tb_sentence_gen.insert("1.0", prompts.get("sentence_generation", ""))
            self.tb_audio_inst.insert("1.0", prompts.get("audio_instructions", ""))
            self.tb_global_words.insert("1.0", prompts.get("global_words_addon", ""))
            self.tb_bonus_all.insert("1.0", prompts.get("bonus_words_all", ""))
            self.tb_bonus_some.insert("1.0", prompts.get("bonus_words_some", ""))

        except Exception as e:
            self.lbl_settings_status.configure(
                text=f"Warning: Could not load config.yaml", text_color="orange"
            )

    def save_settings(self):
        try:
            env_path = self.get_env_path()
            if not os.path.exists(env_path):
                open(env_path, "w").close()
            set_key(env_path, "OPENAI_API_KEY", self.entry_openai.get().strip())
            set_key(env_path, "ANTHROPIC_API_KEY", self.entry_claude.get().strip())

            with open("config.yaml", "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}

            config.setdefault("anki", {})
            config["anki"]["deck_name"] = self.entry_deck_name.get().strip()

            config.setdefault("defaults", {})
            config["defaults"]["target_language"] = self.entry_target.get().strip()
            config["defaults"]["source_language"] = self.entry_source.get().strip()
            config["defaults"]["level"] = self.entry_level.get().strip()
            config["defaults"]["setting"] = self.entry_setting.get().strip()
            try:
                config["defaults"]["number_of_sentences"] = int(
                    self.entry_sentences.get().strip()
                )
            except ValueError:
                self.lbl_settings_status.configure(
                    text="Error: Sentences must be a number!", text_color="red"
                )
                return

            config.setdefault("model", {})
            config["model"]["sentence_generation"] = self.opt_sentence_provider.get()
            config["model"]["audio"] = self.opt_audio_provider.get()

            config.setdefault("openai", {}).setdefault("sentence_generation", {})
            config["openai"]["sentence_generation"][
                "model_id"
            ] = self.entry_openai_sent_model.get().strip()
            config["openai"].setdefault("audio", {})
            config["openai"]["audio"][
                "model_id"
            ] = self.entry_openai_audio_model.get().strip()
            config["openai"]["audio"]["voices"] = [
                v.strip()
                for v in self.entry_openai_voices.get().split(",")
                if v.strip()
            ]

            config.setdefault("claude", {})
            config["claude"]["model_id"] = self.entry_claude_model.get().strip()

            config.setdefault("edge_tts", {})
            config["edge_tts"]["voices"] = [
                v.strip() for v in self.entry_edge_voices.get().split(",") if v.strip()
            ]

            with open("config.yaml", "w", encoding="utf-8") as f:
                yaml.dump(
                    config,
                    f,
                    allow_unicode=True,
                    default_flow_style=False,
                    sort_keys=False,
                )

            self.lbl_settings_status.configure(
                text="Standard Settings successfully saved!", text_color="green"
            )
            self.after(3000, lambda: self.lbl_settings_status.configure(text=""))

        except Exception as e:
            self.lbl_settings_status.configure(
                text=f"Error saving: {e}", text_color="red"
            )

    def save_advanced_settings(self):
        try:
            with open("config.yaml", "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}

            config.setdefault("anki", {})
            try:
                config["anki"]["model_id"] = int(self.entry_model_id.get().strip())
            except ValueError:
                self.lbl_adv_status.configure(
                    text="Error: Model ID must be a number!", text_color="red"
                )
                return

            config.setdefault("prompts", {})
            config["prompts"]["system_prompt"] = self.tb_system_prompt.get(
                "1.0", "end-1c"
            )
            config["prompts"]["sentence_generation"] = self.tb_sentence_gen.get(
                "1.0", "end-1c"
            )
            config["prompts"]["audio_instructions"] = self.tb_audio_inst.get(
                "1.0", "end-1c"
            )
            config["prompts"]["global_words_addon"] = self.tb_global_words.get(
                "1.0", "end-1c"
            )
            config["prompts"]["bonus_words_all"] = self.tb_bonus_all.get(
                "1.0", "end-1c"
            )
            config["prompts"]["bonus_words_some"] = self.tb_bonus_some.get(
                "1.0", "end-1c"
            )

            with open("config.yaml", "w", encoding="utf-8") as f:
                yaml.dump(
                    config,
                    f,
                    allow_unicode=True,
                    default_flow_style=False,
                    sort_keys=False,
                )

            self.lbl_adv_status.configure(
                text="Advanced Settings successfully saved!", text_color="green"
            )
            self.after(3000, lambda: self.lbl_adv_status.configure(text=""))

        except Exception as e:
            self.lbl_adv_status.configure(
                text=f"Error saving advanced settings: {e}", text_color="red"
            )


def main():
    app = AnkiGeneratorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
