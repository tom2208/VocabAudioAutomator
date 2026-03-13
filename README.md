# VocabAudioAutomator

VocabAudioAutomator is a modular Python pipeline (now featuring a sleek Desktop GUI!) that automates the creation of high-quality, audio-enabled Anki flashcards for language learning. 

Whether you want to fully automate sentence generation using AI or manually write your own sentences and just generate the text-to-speech (TTS) audio, this tool adapts to your workflow and budget.

- [VocabAudioAutomator](#vocabaudioautomator)
  - [✨ Features](#-features)
  - [⚙️ Prerequisites](#️-prerequisites)
  - [🚀 Setup \& Installation](#-setup--installation)
  - [🛠️ How to Use (GUI \& CLI)](#️-how-to-use-gui--cli)
    - [Option A: The Desktop GUI (Recommended)](#option-a-the-desktop-gui-recommended)
    - [Option B: The Command Line Interface (CLI)](#option-b-the-command-line-interface-cli)
  - [📦 Building the Standalone App (.exe)](#-building-the-standalone-app-exe)
  - [📝 Preparing Your Vocabulary (The CSV)](#-preparing-your-vocabulary-the-csv)
    - [The Columns](#the-columns)
    - [The `!GLOBAL` Command](#the-global-command)
    - [Example `vocab.csv`](#example-vocabcsv)
  - [💸 Real-World Costs \& My Experience](#-real-world-costs--my-experience)
    - [The "Smart \& Thrifty" Route (My Personal Choice)](#the-smart--thrifty-route-my-personal-choice)
    - [The "Quality" Route (Adding OpenAI TTS)](#the-quality-route-adding-openai-tts)
  - [💡 Troubleshooting \& Best Practices](#-troubleshooting--best-practices)
  - [⚖️ Legal \& Usage Disclaimer](#️-legal--usage-disclaimer)
  - [📄 License](#-license)

## ✨ Features

* **User-Friendly GUI & CLI:** Run the tool via a modern graphical desktop interface or integrate it into your terminal workflow. No coding knowledge required to adjust settings!
* **AI Sentence Generation:** Feed the script a CSV list of vocabulary words, and it uses the Anthropic Claude API (or OpenAI's GPT models) to generate natural, context-rich sentences with both source and target language translations.
* **High-Quality Audio (TTS):** Generate native-sounding audio for your cards using either:
  * **Microsoft Edge TTS:** Free (for personal use).
  * **OpenAI (gpt-4o / gpt-4o-mini):** Quality AI voices (Requires API key).
* **Automated Anki Deck Creation:** Packages your text and audio into a ready-to-import Anki deck file (`.apkg`).
* **Seamless Merging:** Name the output deck the same as an existing Anki deck, and Anki will automatically add the new cards to it without overwriting your old ones.

## ⚙️ Prerequisites

* Python 3.12+
* Poetry installed
* Anki installed on your machine
* **Optional API Keys:**
  * [Anthropic API Key](https://console.anthropic.com/) (If using Claude for sentence generation)
  * [OpenAI API Key](https://platform.openai.com/) (If using OpenAI for audio generation)

## 🚀 Setup & Installation

1. Clone this repository:
   ```bash
   git clone [https://github.com/tom2208/VocabAudioAutomator.git](https://github.com/tom2208/VocabAudioAutomator.git)
   cd VocabAudioAutomator
   ```

2. Install the dependencies using Poetry:
   ```bash
   poetry install
   ```

3. Configure your Settings (Two ways to do this):
   * **The Easy Way (via GUI):** Just launch the app (see Option A below) and enter your API keys and language preferences directly in the "Settings" tab. The app will save them for you.
   * **The Manual Way:** Create a `.env` file for your API keys (`OPENAI_API_KEY=...` and `ANTHROPIC_API_KEY=...`) and rename `config.yaml.example` to `config.yaml` to adjust your settings manually.

## 🛠️ How to Use (GUI & CLI)

*Note: Always prefix your commands with `poetry run` to ensure they execute inside the correct virtual environment.*

### Option A: The Desktop GUI (Recommended)
Launch the graphical interface with a single command:

```bash
poetry run anki-gui
```

This opens the VocabAudioAutomator App, which features three tabs:
1. **Generator:** Select your vocabulary CSV, choose an output folder, name your Anki deck, and hit "Start Generation". A progress bar will keep you updated.
2. **Settings:** Easily input your API keys, change your target language, adjust the difficulty level, and select your preferred TTS voices.
3. **Advanced (Prompts):** For power users! Edit the exact System Prompts and formatting rules the AI uses, or change the Anki Model ID.

### Option B: The Command Line Interface (CLI)
If you prefer the terminal, you can run the entire pipeline with a single command. 

```bash
poetry run anki-cli vocab.csv -o "my_output_folder" -n "My_Spanish_Cards" -d "Español_Deck"
```

**Available CLI Arguments:**
* `csv_file` (Required): Path to your vocabulary CSV file.
* `-o`, `--output` (Optional): Target directory for generated files (default: 'outputs').
* `-n`, `--name` (Optional): Name of the final `.apkg` file.
* `-d`, `--deck` (Optional): Exact Name of the Target Anki Deck (overrides the `config.yaml`).

## 📦 Building the Standalone App (.exe)

If you want to share this tool with friends who don't have Python installed, or if you just want a convenient double-click application for yourself, you can easily compile the script into a standalone `.exe` using the included `auto-py-to-exe` package.

1. **Run the Converter:**
   In your terminal, run:
   ```bash
   poetry run auto-py-to-exe
   ```

2. **Configure the Build:**
   A new window/app will open. Configure it exactly like this:
   * **Script Location:** Browse and select the included `start.py` file from the main folder.
   * **Onefile:** Select **One Directory** (This is much faster and more reliable than a single huge file).
   * **Console Window:** Select **Window Based (hide the console)**.
   * **Advanced:** Scroll down to the `--collect-all` field, click the `+` icon and type `customtkinter`.

3. **Convert & Finalize:**
   * Click the big blue **Convert .py to .exe** button. 
   * Once finished, open the output folder. 
   * **Crucial Step:** Copy your `config.yaml`, a blank `.env` file (remove your API keys before sharing!), and a sample `vocab.csv` into this new output folder, right next to the `.exe`. 
   
You can now zip this folder and share it! Anyone can just double-click the `.exe` to run the GUI.

## 📝 Preparing Your Vocabulary (The CSV)
Before running the AI pipeline, you need to tell it what words to generate sentences for. This is done using a `.csv` file. 

The CSV file uses specific columns allowing you to customize the AI's output on a word-by-word basis. Only the `word` column is strictly required; the rest can be left blank to use the defaults from your settings.

### The Columns
* `word`: (Required) The target vocabulary word you want to learn.
* `count`: (Optional) How many sentences to generate. If left blank, it uses the default (e.g., 5).
* `bonus_words`: (Optional) Specific extra words you want the AI to include in the sentences (e.g., forcing it to use specific verbs or adjectives alongside your main word).
* `bonus_mode`: (Optional) How strict the AI should be about using the bonus words (options: `all`, `some`).
* `setting`: (Optional) A specific theme or scenario for the sentences (e.g., "At a restaurant", "In a business meeting"). Overrides the default setting. You could also try to ask the AI for grammar specifics, like "use the subjunctive".

### The `!GLOBAL` Command
If you want to apply a specific list of bonus words to your *entire* vocabulary list, you do not need to copy and paste it on every single row. 

Simply type `!GLOBAL` in the `word` column at the top of your file and put your "global" bonus words in the `bonus_words` column separated with a semicolon `;` or whitespace.

### Example `vocab.csv`
```csv
word,count,bonus_words,bonus_mode,setting
!GLOBAL,,,,At an Italian restaurant
evitare,,,,
ordinare,3,vino rosso,all,
riunione,,,all,Corporate office environment
```

## 💸 Real-World Costs & My Experience

If you are worried about API costs draining your bank account, don't be! Paying for the Claude API to generate sentences is incredibly cheap. 

To give you a realistic idea, here is a cost breakdown based on an **ambitious learning schedule: 10 new words a day, with 5 sentences per word (50 sentences/day, or ~1,500 sentences a month).**

*(Note: These estimates do not include local taxes, which vary by region).*

### The "Smart & Thrifty" Route (My Personal Choice)
If you want great flashcards without a monthly subscription fee, use Claude for the text and Edge TTS for the audio.
* **Text Generation (Claude 3.5 Sonnet):** I generated over 100 sentences for about $0.03. At a pace of 1,500 sentences a month, **Claude costs me roughly ~$0.50 per month.** * **Audio Generation (Edge TTS):** **$0.00 (Free).** The pronunciation is accurate and totally fine for learning, even if it isn't the absolute most natural-sounding AI voice out there. I personally stick with this option!
* **Total Cost:** **Under $1.00 a month.**

### The "Quality" Route (Adding OpenAI TTS)
If you want natural, native-sounding voices and don't mind paying a bit more, you can route the audio through OpenAI's TTS models.

* **Option A: `gpt-4o-audio-preview` (The Best Quality)**
  * **Cost:** ~$0.0066 per sentence (In my testing, 18 sentences cost $0.12).
  * **Monthly Estimate (1,500 sentences):** **~$10.00 / month.** * **Verdict:** It is quite expensive, but the audio quality and natural inflection are absolutely incredible.

* **Option B: `gpt-4o-mini-audio-preview` (The Budget AI Voice)**
  * **Cost:** Exactly 4x cheaper than the standard 4o model (based on the price tables of OpenAI).
  * **Monthly Estimate (1,500 sentences):** **~$2.50 / month.**
  * **Verdict:** A great middle-ground, but be aware of minor quirks. In my testing with Italian, it occasionally had rare pronunciation issues (like pronouncing an 'r' slightly like an 'l').

## 💡 Troubleshooting & Best Practices
* **Special Characters Breaking (ß, ä, è, etc.):** If your generated flashcards have weird symbols instead of accents or umlauts, the issue is your CSV encoding. When saving your `vocab.csv` from Excel or LibreOffice, you must select **CSV UTF-8 (Comma delimited)** as the save format.

## ⚖️ Legal & Usage Disclaimer

**1. Unofficial Edge TTS Usage**
The Microsoft Edge TTS functionality in this project relies on an undocumented, reverse-engineered API (via the `edge-tts` package). It is strictly intended for **personal, non-commercial, and educational use**. Generating audio using this method for commercial products, apps, or monetization is a violation of Microsoft's Terms of Service. The author of this repository is not responsible for any bans, IP blocks, or legal action taken by Microsoft as a result of abusing this endpoint.

**2. AI-Generated Content**
This tool uses AI models (Anthropic Claude and OpenAI) to generate text and audio. The author makes no guarantees regarding the accuracy, grammatical correctness, or cultural appropriateness of the generated flashcard sentences. You are responsible for reviewing the generated content and adhering to the Acceptable Use Policies of Anthropic and OpenAI.

**3. No Affiliation**
This project is an independent open-source tool. It is not affiliated with, endorsed by, or maintained by Ankitects (the creators of Anki), Microsoft, OpenAI, or Anthropic.

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for more details.