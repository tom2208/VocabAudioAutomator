# VocabAudioAutomator

VocabAudioAutomator is a modular Python pipeline that automates the creation of high-quality, audio-enabled Anki flashcards for language learning. 

Whether you want to fully automate sentence generation using AI or manually write your own sentences and just generate the text-to-speech (TTS) audio, this tool adapts to your workflow and budget.

## ✨ Features

* **AI Sentence Generation:** Feed the script a CSV list of vocabulary words, and it uses the Anthropic Claude API to generate natural, context-rich sentences with both source and target language translations. *(Note: Other LLMs coming soon).*
* **High-Quality Audio (TTS):** Generate native-sounding audio for your cards using either:
  * **Microsoft Edge TTS:** Free (for personal use).
  * **OpenAI (gpt-4o / gpt-4o-mini):** Quality AI voices (Requires API key).
* **Automated Anki Deck Creation:** Packages your text and audio into a ready-to-import Anki deck file. Just double-click the output file to add it to Anki!
* **Seamless Merging:** Name the output deck the same as an existing Anki deck, and Anki will automatically add the new cards to it (without overwriting your old ones).
* **Modular & Skippable Steps:** Don't want to pay for Claude? You can write your own sentences in the required format, drop them in the source folder, and use Edge TTS to generate a completely free audio deck.

## ⚙️ Prerequisites

* Python 3.12+
* Anki installed on your machine
* **Optional API Keys:**
  * [Anthropic API Key](https://console.anthropic.com/) (If using Claude for sentence generation)
  * [OpenAI API Key](https://platform.openai.com/) (If using OpenAI for audio generation)

## 🚀 Setup & Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/tom2208/VocabAudioAutomator.git
   cd VocabAudioAutomator

2. Install the dependencies using Poetry:
    ```bash
    poetry install
    ```

3. Set up your API Keys (Secrets):
    Create a `.env` file in the root directory and add your API keys. Never share this file or upload it to GitHub:
    ```
    OPENAI_API_KEY=sk-proj-...
    ANTHROPIC_API_KEY=sk-ant-...
    ```

4. Configure your Settings:
    Copy the config.yaml.example file and rename it to `config.yaml`. Adjust your target language, difficulty level, and preferred TTS voices here.

## 📝 Preparing Your Vocabulary (The CSV)
Before running the AI pipeline, you need to tell it what words to generate sentences for. This is done using the `vocab.csv` file. The file must be in the same directory as the `.py` scripts.

The CSV file uses specific columns allowing you to customize the AI's output on a word-by-word basis. Only the word column is strictly required; the rest can be left blank to use the defaults from your `config.yaml`.

### The Columns
* `word`: (Required) The target vocabulary word you want to learn.

* `count`: (Optional) How many sentences to generate. If left blank, it uses the default (5) from `config.yaml`.

* `bonus_words`: (Optional) Specific extra words you want the AI to include in the sentences (e.g., forcing it to use specific verbs or adjectives alongside your main word).

* `bonus_mode`: (Optional) How strict the AI should be about using the bonus words (options: all, some).

* `setting`: (Optional) A specific theme or scenario for the sentences (e.g., "At a restaurant", "In a business meeting"). Overrides the default setting. You could also try to ask the AI for grammar or anything else, like "use the subjunctive".

### The `!GLOBAL` Command
If you want to apply a specific list of bonus words to your *entire* vocabulary list, you do not need to copy and paste it on every single row. 

Simply type `!GLOBAL` in the `word` column at the top of your file and put your "global" bonus words in the `bonus_words` column separated with a semicolon `;` or whitespace. This way you don't need to copy your bonus words into every row. Specially useful for long lists.

### Example `vocab.csv`
```csv
word,       count,  bonus_words,    bonus_mode, setting
!GLOBAL,    ,       ,               ,           At an Italian restaurant
evitare,    ,       ,               ,
ordinare,   3,      vino rosso,     all,
riunione,   ,       ,               all,        Corporate office environment
```

## 🛠️ How to Use (The Pipeline)
You can run the entire pipeline at once using the master script, or run individual scripts depending on your needs.

*Note: Prefix your commands with poetry run to ensure they execute inside the virtual environment.*

### Option A: The Full Automated Pipeline
Place your target vocabulary words in the `vocab.csv` file.

Run the master script:

```bash
poetry run python run_all.py
```
The script will sequentially generate sentences -> generate audio -> package the .apkg file.

Double-click the generated .apkg file to import it into Anki.

### Option B: The Free Route (Manual Sentences + Edge TTS)
If you prefer to write your own sentences, you can skip the LLM costs entirely!

1. Write your sentences in the required format and save them in the `source/` folder as a `.txt`. You can even split the sentence among different files, the script will just take the content of all `.txt` files and process it. So delete all `.txt` files you don't want to be converted into Anki cards.
    The correct format for the `.txt` files is:

    ```
    target language sentence 1 | source language translation sentence 1
    target language sentence 2 | source language translation sentence 2
    ...
    ```

2. Ensure your audio model in the config.yaml is set to use `edge_tts`.
3. If you want to import your cards into an existing deck make sure you use the exact same name (case sensitive).

4. Run the audio and deck generation scripts:

    ```bash
    poetry run python gen_audio.py
    poetry run python build_deck.py
    ```
5. The script has now created a `AI_Generated_Sentences.apkg` file you can just double-click it to import it into Anki or do it manually. If you set the correct name the cards will be imported into the desired deck. You can delete the content of the `output/` directory now.

**Hint** you could ask a free LLM to produce sentences in the desired format and just copy and paste them into a `.txt` file. Feel free to use the prompt in the `config.yaml` for that.

## 💸 Real-World Costs & My Experience

If you are worried about API costs draining your bank account, don't be! Paying for the Claude API to generate sentences is incredibly cheap. 

To give you a realistic idea, here is a cost breakdown based on an **ambitious learning schedule: 10 new words a day, with 5 sentences per word (50 sentences/day, or ~1,500 sentences a month).**

*(Note: These estimates do not include local taxes, which vary by region).*

### The "Smart & Thrifty" Route (My Personal Choice)
If you want great flashcards without a monthly subscription fee, use Claude for the text and Edge TTS for the audio.
* **Text Generation (Claude 3.6 Sonnet):** I generated over 100 sentences for about $0.03. At a pace of 1,500 sentences a month, **Claude costs me roughly ~$0.50 per month.**  
* **Audio Generation (Edge TTS):** **$0.00 (Free).** The pronunciation is accurate and totally fine for learning, even if it isn't the absolute most natural-sounding AI voice out there. I personally stick with this option!
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
* Special Characters Breaking (ß, ä, è, etc.): If your generated flashcards have weird symbols instead of accents or umlauts, the issue is your CSV encoding. When saving your `vocab.csv` from Excel or LibreOffice, you must select CSV UTF-8 (Comma delimited) as the save format.

## ⚖️ Legal & Usage Disclaimer

**1. Unofficial Edge TTS Usage**
The Microsoft Edge TTS functionality in this project relies on an undocumented, reverse-engineered API (via the `edge-tts` package). It is strictly intended for **personal, non-commercial, and educational use**. Generating audio using this method for commercial products, apps, or monetization is a violation of Microsoft's Terms of Service. The author of this repository is not responsible for any bans, IP blocks, or legal action taken by Microsoft as a result of abusing this endpoint.

**2. AI-Generated Content**
This tool uses AI models (Anthropic Claude and OpenAI) to generate text and audio. The author makes no guarantees regarding the accuracy, grammatical correctness, or cultural appropriateness of the generated flashcard sentences. You are responsible for reviewing the generated content and adhering to the Acceptable Use Policies of Anthropic and OpenAI.

**3. No Affiliation**
This project is an independent open-source tool. It is not affiliated with, endorsed by, or maintained by Ankitects (the creators of Anki), Microsoft, OpenAI, or Anthropic.

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for more details.
