class GUIStrings:

    VERSION = "v1.0.0"
    APP_TITLE = f"Vocab Audio Automator {VERSION}"
    GEN_TAB_NAME = "Generator"
    SETTINGS_TAB_NAME = "Settings"
    ADVANDCED_TAB_NAME = "Advanced"

    # tab: generation
    ## buttons
    BUTTON_LABEL_CSV = "Select CSV File"
    BUTTON_LABEL_OUTPUT = "Select Output Folder"
    BUTTON_START_GENERATION = "Start Generation"
    ## labels
    LABEL_GENERATOR_TAB_TITLE = "Anki Card Generator"
    LABEL_AUDIO_ONLY_TOGGLE_TITLE = "Audio & Deck Only Mode (Skip AI Text Generation)"
    LABEL_NO_FILE_SELECTED = "No File selected"
    LABEL_OUTPUT_DIRECTORY = "Output directory: ./{dir}"
    LABEL_ANKI_DECK_NAME = "Exact Target Anki Deck Name:"
    LABEL_OUTPUT_NAME = "Name of the Output File:"
    ## placeholder
    PLACEHOLDER_DECK_NAME = "e.g. Italiano"
    PLACEHOLDER_FILE_NAME = "e.g. Italian_Week_1"

    # tab: settings
    ## labels
    LABEL_API_KEYS = "API Keys"
    LABEL_OPENAI_KEY = "OpenAI API Key:"
    LABEL_ANTHROPIC_KEY = "Anthropic API Key:"
    LABEL_LANGUAGE_DEFAULTS_TITLE = "Language Defaults"
    LABEL_TARGET_LANGUAGE = "Target Language (The language you are learning):"
    LABEL_SOURCE_LANGUAGE = "Source Language (Your native/translation language):"
    LABEL_LANGUAGE_LEVEL = "Language Level:"
    LABEL_NUM_SENTENCES = "Default Number of Sentences:"
    LABEL_SETTING = "Setting / Context:"
    LABEL_LLM_PROVIDERS_TITLE = "LLM Providers"
    LABEL_SENTENCE_PROVIDER = "Sentence Generation Provider:"
    ## placeholder
    PLACEHOLDER_OPENAI_KEY = "sk-..."
    PLACEHOLDER_ANTHROPIC_KEY = "sk-ant-..."
    PLACEHOLDER_TARGET_LANGUAGE = "e.g. Italian"
    PLACEHOLDER_SOURCE_LANGUAGE = "e.g. English"
    PLACEHOLDER_LANGUAGE_LEVEL = "e.g. A2"
    PLACEHOLDER_NUM_SENTENCES = "e.g. 5"
    PLACEHOLDER_SETTING = "e.g. General context"
