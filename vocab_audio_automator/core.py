import os
import csv
import sys
import time
import yaml
import random
import base64
import asyncio
from datetime import datetime
from pathlib import Path

import genanki
import edge_tts
from openai import OpenAI
from anthropic import Anthropic
from dotenv import load_dotenv

################################
# Configuration & Setup        #
################################


def load_config(config_path="config.yaml"):
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise Exception(f"Configuration file '{config_path}' not found.")
    except yaml.YAMLError as exc:
        raise Exception(f"Error parsing YAML config: {exc}")


def initialize_clients(config):
    # Ensure we look for the .env in the exact same directory as the executable/script
    if getattr(sys, "frozen", False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.getcwd()

    env_path = os.path.join(base_dir, ".env")
    load_dotenv(dotenv_path=env_path, override=True)

    active_ai = config.get("model", {}).get("sentence_generation", "openai").lower()
    clients = {}

    if active_ai == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise Exception(f"Missing OPENAI_API_KEY in {env_path}")
        clients["openai"] = OpenAI(api_key=api_key)

    elif active_ai == "claude":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise Exception(f"Missing ANTHROPIC_API_KEY in {env_path}")
        clients["claude"] = Anthropic(api_key=api_key)
    else:
        raise Exception(f"Invalid sentence_generation model in config: {active_ai}.")

    return clients, active_ai


################################
# Utility Functions            #
################################


def get_data_from_file(file_path, status_callback=print):
    status_callback(f"Reading txt data from file: {file_path}")
    results = []

    if not os.path.exists(file_path):
        raise Exception(f"The file '{file_path}' was not found.")

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            clean_line = line.strip()
            if "|" in clean_line:
                target, source = clean_line.split("|", 1)
                results.append((target.strip(), source.strip()))

    return results


def gen_unique_filename(base_name="audio", extension=".mp3"):
    timestamp = int(time.time() * 1000)
    return f"{base_name}_{timestamp}{extension}"


################################
# Data Processing & Prompts    #
################################


def process_vocabulary(csv_path):
    global_words_string = ""
    vocab_to_process = []

    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                word = row.get("word", "").strip()
                if not word:
                    continue
                if word.upper() == "!GLOBAL":
                    global_words_string = row.get("bonus_words", "").strip()
                    continue
                vocab_to_process.append(row)
    except FileNotFoundError:
        raise Exception(f"CSV file '{csv_path}' not found.")

    return vocab_to_process, global_words_string


def build_prompts(vocab_to_process, global_words_string, config, status_callback=print):
    final_prompts = {}
    global_text = ""

    if global_words_string:
        global_text = config["prompts"]["global_words_addon"].format(
            global_words=global_words_string
        )

    for row in vocab_to_process:
        word = row.get("word", "").strip()

        raw_count = row.get("count", "").strip()
        try:
            target_count = (
                int(raw_count)
                if raw_count
                else config["defaults"]["number_of_sentences"]
            )
        except ValueError:
            target_count = config["defaults"]["number_of_sentences"]

        status_callback(
            f"--> INFO: Requesting exactly {target_count} sentence(s) for '{word}'."
        )

        local_text = ""
        bonus_words = row.get("bonus_words", "").strip()
        if bonus_words:
            mode = row.get("bonus_mode", "").strip() or "all"
            if mode == "all":
                local_text = config["prompts"]["bonus_words_all"].format(
                    extra_words=bonus_words
                )
            elif mode == "some":
                local_text = config["prompts"]["bonus_words_some"].format(
                    extra_words=bonus_words
                )

        combined_optional_instructions = f"{global_text}\n{local_text}".strip()
        row_setting = row.get("setting", "").strip()
        final_setting = row_setting if row_setting else config["defaults"]["setting"]

        final_prompt = config["prompts"]["sentence_generation"].format(
            number_of_sentences=target_count,
            target_language=config["defaults"]["target_language"],
            source_language=config["defaults"]["source_language"],
            language_level=config["defaults"]["level"],
            setting=final_setting,
            target_word=word,
            optional_instruction=combined_optional_instructions,
        )

        final_prompt += f"\n\nCRITICAL SYSTEM OVERRIDE: You MUST output EXACTLY {target_count} sentence pair(s). Do NOT output more. Do NOT output less."
        final_prompts[word] = final_prompt

    return final_prompts


def fetch_ai_completion(
    clients,
    active_ai,
    config,
    system_prompt,
    user_prompt,
    status_callback,
    max_retries=3,
):
    for attempt in range(max_retries):
        try:
            if active_ai == "openai":
                model_id = config["openai"]["sentence_generation"]["model_id"]
                response = clients["openai"].chat.completions.create(
                    model=model_id,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                )
                return response.choices[0].message.content

            elif active_ai == "claude":
                model_id = config["claude"]["model_id"]
                max_tokens = config.get("claude", {}).get("max_tokens", 1000)
                response = clients["claude"].messages.create(
                    model=model_id,
                    max_tokens=max_tokens,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}],
                )
                return response.content[0].text

        except Exception as e:
            status_callback(f"  [!] Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                status_callback("  [*] Waiting 5 seconds before retrying...")
                time.sleep(5)
            else:
                status_callback(f"  [X] Max retries reached. Moving to next word.")
                return None


################################
# Audio Generation             #
################################


def generate_audio_edge(text, filename, edge_tts_voices):
    voice = random.choice(edge_tts_voices)

    async def _generate():
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(filename)

    asyncio.run(_generate())
    return voice


def generate_audio_gpt4o(client, text, filename, config):
    model_id = config["openai"]["audio"]["model_id"]
    voice = random.choice(config["openai"]["audio"]["voices"])
    audio_instructions = config["prompts"]["audio_instructions"]

    response = client.chat.completions.create(
        model=model_id,
        modalities=["text", "audio"],
        audio={"voice": voice, "format": "mp3"},
        messages=[
            {"role": "system", "content": audio_instructions},
            {
                "role": "user",
                "content": f"Repeat this text exactly word-for-word: {text}",
            },
        ],
    )

    audio_data_b64 = response.choices[0].message.audio.data
    with open(filename, "wb") as f:
        f.write(base64.b64decode(audio_data_b64))
    return voice


################################
# MAIN PIPELINE                #
################################


def run_pipeline(
    input_path,
    output_dir="outputs",
    output_name="AI_Generated_Sentences",
    target_deck_name=None,
    run_audio_only=False,
    status_callback=print,
    progress_callback=None,
):
    try:
        # --- PHASE 0: SETUP ---
        status_callback("Loading configuration...")
        config = load_config()

        # Only initialize text generation clients if we are NOT in audio-only mode
        if not run_audio_only:
            clients, active_ai = initialize_clients(config)
            system_prompt = config["prompts"]["system_prompt"]
        else:
            # We still need clients for audio if using OpenAI TTS, but we will init it below.
            clients = {}
            active_ai = "none"

        audio_folder = os.path.join(output_dir, "audio")
        os.makedirs(audio_folder, exist_ok=True)
        current_step = 0

        # --- PHASE 1: SENTENCE GENERATION (Or Bypass) ---
        if not run_audio_only:
            status_callback(f"Reading vocabulary from: {input_path}")
            vocab_to_process, global_words_string = process_vocabulary(input_path)
            final_prompts = build_prompts(
                vocab_to_process, global_words_string, config, status_callback
            )

            total_steps = (len(final_prompts) * 2) + 1
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = os.path.join(
                output_dir, f"{active_ai}_output_{timestamp}.txt"
            )

            with open(output_filename, "a", encoding="utf-8") as output_file:
                for i, (word, prompt) in enumerate(final_prompts.items()):
                    status_callback(
                        f"Generating sentences for '{word}' ({i+1}/{len(final_prompts)})..."
                    )
                    result_text = fetch_ai_completion(
                        clients,
                        active_ai,
                        config,
                        system_prompt,
                        prompt,
                        status_callback,
                    )
                    if result_text:
                        output_file.write(result_text + "\n")

                    current_step += 1
                    if progress_callback:
                        progress_callback(current_step / total_steps)
                    time.sleep(1)
        else:
            status_callback(
                f"Skipping Sentence Generation. Using provided text file..."
            )
            output_filename = input_path  # The input file IS the text file

        # --- PHASE 2: AUDIO GENERATION ---
        status_callback("Fetching sentences for audio creation...")
        results = get_data_from_file(output_filename, status_callback)

        if run_audio_only:
            total_steps = len(results) + 1  # Calculate progress bar for audio-only mode

        audio_model = config["model"]["audio"]
        target_language = config["defaults"]["target_language"]
        look_up_list = []

        if audio_model == "openai" and "openai" not in clients:
            if getattr(sys, "frozen", False):
                base_dir = os.path.dirname(sys.executable)
            else:
                base_dir = os.getcwd()
            env_path = os.path.join(base_dir, ".env")
            load_dotenv(dotenv_path=env_path, override=True)

            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise Exception(
                    f"Missing OPENAI_API_KEY in {env_path} for Audio Generation."
                )
            clients["openai"] = OpenAI(api_key=api_key)

        status_callback(f"Generating audio using '{audio_model}'...")
        for i, (target, source) in enumerate(results):
            file_name = gen_unique_filename(base_name=target_language.replace(" ", "_"))
            file_path = os.path.join(audio_folder, file_name)

            status_callback(f"Audio ({i+1}/{len(results)}): {target[:30]}...")

            if audio_model == "openai":
                voice = generate_audio_gpt4o(
                    clients["openai"], target, file_path, config
                )
            elif audio_model == "edge_tts":
                edge_tts_voices = config["edge_tts"]["voices"]
                voice = generate_audio_edge(target, file_path, edge_tts_voices)
            else:
                raise Exception(f"Unsupported audio model '{audio_model}' in config.")

            look_up_list.append((target, source, file_path, voice))

            current_step += 1
            if progress_callback:
                progress_callback(current_step / total_steps)

        lookup_path = os.path.join(audio_folder, "lookup_list.txt")
        with open(lookup_path, "w", encoding="utf-8") as f:
            for target, source, audio_path, voice in look_up_list:
                f.write(f"{target} | {source} | {audio_path} | {voice}\n")

        # --- PHASE 3: ANKI DECK CREATION ---
        status_callback("Packaging Anki Deck...")
        model_id = config["anki"]["model_id"]
        final_deck_name = (
            target_deck_name if target_deck_name else config["anki"]["deck_name"]
        )

        my_model = genanki.Model(
            model_id,
            final_deck_name,
            fields=[{"name": "Front"}, {"name": "Back"}, {"name": "Audio"}],
            templates=[
                {
                    "name": "Card 1",
                    "qfmt": "{{Front}}<br><br>{{Audio}}",
                    "afmt": '{{FrontSide}}<hr id="answer">{{Back}}',
                }
            ],
            css=".card { font-family: arial; font-size: 20px; text-align: center; color: black; background-color: white; }",
        )

        my_deck = genanki.Deck(random.randrange(1 << 30, 1 << 31), final_deck_name)
        media_files_to_export = []

        for item in look_up_list:
            front_text, back_text, audio_path, _ = item
            audio_filename = os.path.basename(audio_path)
            my_note = genanki.Note(
                model=my_model,
                fields=[front_text, back_text, f"[sound:{audio_filename}]"],
                guid=genanki.guid_for(front_text),
            )
            my_deck.add_note(my_note)
            if os.path.exists(audio_path):
                media_files_to_export.append(audio_path)
            else:
                status_callback(f"Warning: Audio file not found: {audio_path}")

        clean_name = output_name.strip()
        if not clean_name.endswith(".apkg"):
            clean_name += ".apkg"

        output_apkg = os.path.join(output_dir, clean_name)
        my_package = genanki.Package(my_deck)
        my_package.media_files = media_files_to_export
        my_package.write_to_file(output_apkg)

        status_callback(f"Success! Deck created: {output_apkg}")

        if progress_callback:
            progress_callback(1.0)
        return True

    except Exception as e:
        status_callback(f"ERROR: {str(e)}")
        return False
