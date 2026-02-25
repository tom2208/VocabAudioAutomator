from datetime import datetime
import time
import yaml
import sys
import os
import csv
from anthropic import Anthropic
from dotenv import load_dotenv

################################
# Configurations and Constants #
################################


def load_config(config_path="config.yaml"):
    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: {config_path} not found.")
        sys.exit(1)
    except yaml.YAMLError as exc:
        print(f"Error parsing YAML: {exc}")
        sys.exit(1)


config = load_config()
load_dotenv()

claude_api_key = os.getenv("ANTHROPIC_API_KEY")
claude_model_id = config["claude"]["model_id"]
claude_max_tokens = config["claude"]["max_tokens"]

system_prompt = config["prompts"]["system_prompt"]
prompt_template = config["prompts"]["sentence_generation"]

if not claude_api_key:
    raise ValueError("Missing ANTHROPIC API key! Please check your .env file.")

########################################################
#  Processing Vocabulary CSV and Handling Global Words #
########################################################

global_words_string = ""
vocab_to_process = []

with open("vocab.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        word = row["word"].strip()
        if not word:
            continue

        if word.upper() == "!GLOBAL":
            global_words_string = row.get("bonus_words", "").strip()
            continue

        vocab_to_process.append(row)

###############################################
# Generating Prompts for Each Word in the CSV #
###############################################

final_prompts = {}

global_text = ""
if global_words_string:
    global_text = config["prompts"]["global_words_addon"].format(
        global_words=global_words_string
    )


for row in vocab_to_process:
    word = row["word"].strip()
    target_count = (
        int(row["count"])
        if row.get("count")
        else config["defaults"]["number_of_sentences"]
    )

    local_text = ""
    if row.get("bonus_words"):
        extra_words = row["bonus_words"]
        mode = row.get("bonus_mode") if row.get("bonus_mode") else "all"

        if mode == "all":
            local_text = config["prompts"]["bonus_words_all"].format(
                extra_words=extra_words
            )
        elif mode == "some":
            local_text = config["prompts"]["bonus_words_some"].format(
                extra_words=extra_words
            )

    combined_optional_instructions = f"{global_text}\n{local_text}".strip()

    final_prompt = config["prompts"]["sentence_generation"].format(
        number_of_sentences=target_count,
        target_language=config["defaults"]["target_language"],
        source_language=config["defaults"]["source_language"],
        language_level=config["defaults"]["level"],
        setting=config["defaults"]["setting"],
        target_word=word,
        optional_instruction=combined_optional_instructions,
    )
    final_prompts[word] = final_prompt

print(f"\nAll {len(final_prompts)} prompts generated and ready for Claude.")


#############################
# Sending Prompts to Claude #
#############################

os.makedirs("outputs", exist_ok=True)

client = Anthropic(api_key=claude_api_key)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_filename = f"outputs/claude_output_{timestamp}.txt"

with open(
    output_filename, "a", encoding="utf-8"
) as output_file:  # Note: Changed "w" to "a" (append) just in case!
    for word, prompt in final_prompts.items():
        print(f"Sending prompt for word: {word}")

        max_retries = 3

        for attempt in range(max_retries):
            try:
                message = client.messages.create(
                    model=claude_model_id,
                    max_tokens=claude_max_tokens,
                    system=system_prompt,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                )

                output_file.write(message.content[0].text + "\n")
                print(f"Response received for word: {word}\n")

                time.sleep(1)
                break

            except Exception as e:
                print(f"  [!] Attempt {attempt + 1} failed: {e}")

                if attempt < max_retries - 1:
                    print("  [*] Server is busy. Waiting 5 seconds before retrying...")
                    time.sleep(5)
                else:
                    print(
                        f"  [X] Giving up on '{word}' after {max_retries} attempts. Moving to next word.\n"
                    )

print(f"Results saved to: {output_filename}")
