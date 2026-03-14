class GUIStrings:

    VERSION = "v1.0.0"
    APP_TITLE = f"Vocab Audio Automator {VERSION}"
    GEN_TAB_NAME = "Generator"
    SETTINGS_TAB_NAME = "Settings"
    ADVANDCED_TAB_NAME = "Advanced"

    # tab: generation
    ## title
    LABEL_GENERATOR_TAB_TITLE = "Anki Card Generator"

    ## toggle
    LABEL_AUDIO_ONLY_TOGGLE_TITLE = "Audio & Deck Only Mode (Skip AI Text Generation)"

    ## open file
    ### open csv
    BUTTON_CSV = "Select CSV File"
    LABEL_NO_FILE_SELECTED = "No File selected"

    ### open txt
    BUTTON_TXT = "Select Sentence File (.txt)"
    LABEL_FORMAT_REQUIRED = "Format required: Target | Source"

    ## output folder
    BUTTON_OUTPUT = "Select Output Folder"
    LABEL_OUTPUT_DIRECTORY = "Output directory: ./{dir}"

    ## deck name
    LABEL_ANKI_DECK_NAME = "Exact Target Anki Deck Name:"
    PLACEHOLDER_DECK_NAME = "e.g. Italiano"

    ## output file name
    LABEL_OUTPUT_NAME = "Name of the Output File:"
    PLACEHOLDER_FILE_NAME = "e.g. Italian_Week_1"

    ## start button
    BUTTON_START_GENERATION = "Start Generation"
    ### errors
    LABEL_ERROR_SELECT_FILE = "Please select an input file first!"
    LABEL_ERROR_TXT_FILE = "Error: Audio-only mode requires a .txt file!"
    LABEL_ERROR_CSV_FILE = "Error: AI Generation requires a .csv file!"
    LABEL_ERROR_INVALID_TXT = "Error: Invalid TXT! Missing 'Target | Source' format."
    LABEL_ERROR_WORD_COLUMN = (
        "Error: CSV must contain a 'word' column in the first row!"
    )
    LABEL_GENERAL_ERROR = "Error reading file: {exc}"
    LABEL_ERROR_ANKI_NAME = "Please enter an Anki Deck Name!"
    LABEL_ERROR_OUTPUT_NAME = "Please enter a valid Output Filename!"
    ### success
    LABEL_GENERATION_SUCCESS = "Successfully finished! {file}.apkg created."

    # tab: settings
    ## api keys
    LABEL_API_KEYS_TITLE = "API Keys"

    LABEL_OPENAI_KEY = "OpenAI API Key:"
    PLACEHOLDER_OPENAI_KEY = "sk-..."

    LABEL_ANTHROPIC_KEY = "Anthropic API Key:"
    PLACEHOLDER_ANTHROPIC_KEY = "sk-ant-..."

    ## language defaults
    LABEL_LANGUAGE_DEFAULTS_TITLE = "Language Defaults"

    LABEL_TARGET_LANGUAGE = "Target Language (The language you are learning):"
    PLACEHOLDER_TARGET_LANGUAGE = "e.g. Italian"

    LABEL_SOURCE_LANGUAGE = "Source Language (Your native/translation language):"
    PLACEHOLDER_SOURCE_LANGUAGE = "e.g. English"

    LABEL_LANGUAGE_LEVEL = "Language Level:"
    PLACEHOLDER_LANGUAGE_LEVEL = "e.g. A2"

    LABEL_NUM_SENTENCES = "Default Number of Sentences:"
    PLACEHOLDER_NUM_SENTENCES = "e.g. 5"

    LABEL_SETTING = "Setting / Context:"
    PLACEHOLDER_SETTING = "e.g. General context"

    ## LLM providers
    LABEL_LLM_PROVIDERS_TITLE = "LLM Providers"
    LABEL_SENTENCE_PROVIDER = "Sentence Generation Provider:"
    LABEL_AUDIO_PROVIDER = "Audio Generation Provider:"

    ## model details
    LABEL_MODEL_DETAILS = "Model Details"

    LABEL_OPENAI_MODEL_ID = "OpenAI Text Model ID:"
    PLACEHOLDER_OPENAI_MODEL_ID = "e.g. gpt-4o-mini"

    LABEL_OPENAI_AUDIO_ID = "OpenAI Audio/TTS Model ID:"
    PLACEHOLDER_OPENAI_AUDIO_ID = "e.g. gpt-4o-audio-preview"

    LABEL_OPENAI_VOICES = "OpenAI Voices"
    PLACEHOLDER_OPENAI_VOICES = "e.g. alloy, echo"

    LABEL_CLAUDE_MODEL_ID = "Claude Text Model ID:"
    PLACEHOLDER_CLAUDE_MODEL_ID = "e.g. claude-3-5-sonnet-20241022"

    LABEL_EDGE_TTS_VOICES = "Edge TTS Voices:"
    PLACEHOLDER_EDGE_TTS_VOICES = "e.g. it-IT-DiegoNeural"

    ## save settings
    BUTTON_SAVE_SETTINGS = "Save Settings"
    LABEL_SETTINGS_SAVED = (
        "Settings successfully saved!"  # also used for the advanced tab
    )
    LABEL_ERROR_SAVING = (
        "Error saving settings: {exc}"  # also used for the advanced tab
    )

    # advanced tab
    LABEL_ANKI_CONFIG = "Technical Anki Config"
    LABEL_ANKI_DECK_ID = "Anki Model ID (Deck Template ID):"

    ## main prompt templates
    LABEL_MAIN_PROMPT = "Main Prompt Templates"
    LABEL_SYSTEM_PROMPT = "System Prompt (Behavior limits):"
    LABEL_SENTENCE_PROMPT = "Sentence Generation Prompt (Structure):"
    LABEL_AUDIO_INSTRUCTIONS = "Audio Instructions (TTS Behavior):"

    ## modular prompt add-ons
    LABEL_MODULAR_PROMPTS = "Modular Prompt Add-ons"
    LABEL_GLOBAL_WORDS = "Global Words Add-on:"
    LABEL_BONUS_WORDS_ALL = "Bonus Words (All mode):"
    LABEL_BONUS_WORDS_SOME = "Bonus Words (Some mode):"

    ## save settings
    BUTTON_SAVE_ADVANCED = "Save Advanced Settings"
    LABEL_ERROR_ANKI_MODEL_ID = "Error: Model ID must be a number!"


class CLIStrings:
    MAIN_DESCRIPTION = "Generates Anki Cards with Audio via LLMs."
    ARG_INPUT_FILE_HELP = "Path to the vocabulary CSV or text file"
    ARG_OUTPUT_FILE_HELP = "Target directory for generated files (default: 'outputs')"
    ARG_NAME_HELP = "Name of the final .apkg file"
    ARG_DECK_HELP = "Exact Name of the Target Anki Deck (Overrides config)"
    ARG_AUDIO_ONLY_HELP = "Skip text generation, read input_file as target|source text"
    START_INFO = "--- Starting Anki Generator CLI ---"
