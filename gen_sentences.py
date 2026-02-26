import os
import sys
import csv
import time
import yaml
from datetime import datetime
from openai import OpenAI
from anthropic import Anthropic
from dotenv import load_dotenv

################################
# Configuration & Setup        #
################################

def load_config(config_path="config.yaml"):
    """Loads the YAML configuration file."""
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: {config_path} not found.")
        sys.exit(1)
    except yaml.YAMLError as exc:
        print(f"Error parsing YAML: {exc}")
        sys.exit(1)

def initialize_clients(config):
    """Initializes the correct AI client based on the sentence_generation config."""
    load_dotenv()
    
    # Read the active sentence generation model from the new config structure
    active_ai = config.get("model", {}).get("sentence_generation", "openai").lower()
    clients = {}

    if active_ai == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Missing OPENAI_API_KEY in .env file.")
        clients["openai"] = OpenAI(api_key=api_key)
        print("Initialized OpenAI Client for Sentence Generation")
        
    elif active_ai == "claude":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("Missing ANTHROPIC_API_KEY in .env file.")
        clients["claude"] = Anthropic(api_key=api_key)
        print("Initialized Claude Client for Sentence Generation")
        
    else:
        raise ValueError(f"Invalid sentence_generation model in config: {active_ai}. Must be 'openai' or 'claude'.")

    return clients, active_ai

################################
# Data Processing & Prompts    #
################################

def process_vocabulary(csv_path="vocab.csv"):
    """Reads the vocabulary CSV and separates global words from target words."""
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
        print(f"Error: {csv_path} not found.")
        sys.exit(1)

    return vocab_to_process, global_words_string

def build_prompts(vocab_to_process, global_words_string, config):
    """Generates the final prompt strings for each vocabulary word."""
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
            mode = row.get("bonus_mode", "all")

            if mode == "all":
                local_text = config["prompts"]["bonus_words_all"].format(extra_words=extra_words)
            elif mode == "some":
                local_text = config["prompts"]["bonus_words_some"].format(extra_words=extra_words)

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

    return final_prompts

################################
# API Interaction & Execution  #
################################

def fetch_ai_completion(clients, active_ai, config, system_prompt, user_prompt, max_retries=3):
    """Routes the prompt to the chosen AI provider using the new nested config keys."""
    for attempt in range(max_retries):
        try:
            if active_ai == "openai":
                # Updated to use the nested 'sentence_generation' keys
                model_id = config["openai"]["sentence_generation"]["model_id"]
                max_tokens = config["openai"]["sentence_generation"]["max_tokens"]
                
                response = clients["openai"].chat.completions.create(
                    model=model_id,
                    max_tokens=max_tokens,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                )
                return response.choices[0].message.content

            elif active_ai == "claude":
                # Updated to map exactly to the 'claude' block in your config
                model_id = config["claude"]["model_id"]
                max_tokens = config["claude"]["max_tokens"]
                
                response = clients["claude"].messages.create(
                    model=model_id,
                    max_tokens=max_tokens,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": user_prompt}
                    ]
                )
                return response.content[0].text

        except Exception as e:
            print(f"  [!] Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print("  [*] Waiting 5 seconds before retrying...")
                time.sleep(5)
            else:
                print(f"  [X] Max retries reached. Moving to next word.\n")
                return None

def main():
    """Main orchestration function."""
    # 1. Setup Config & Clients
    config = load_config()
    clients, active_ai = initialize_clients(config)
    system_prompt = config["prompts"]["system_prompt"]

    # 2. Process data and generate prompts
    vocab_to_process, global_words_string = process_vocabulary("vocab.csv")
    final_prompts = build_prompts(vocab_to_process, global_words_string, config)
    print(f"\nAll {len(final_prompts)} prompts generated and ready to be processed by {active_ai.capitalize()}.")

    # 3. Prepare output directory and file
    os.makedirs("outputs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"outputs/{active_ai}_output_{timestamp}.txt"

    # 4. Process prompts and save results
    with open(output_filename, "a", encoding="utf-8") as output_file:
        for word, prompt in final_prompts.items():
            print(f"\nSending prompt for word: {word}")
            
            result_text = fetch_ai_completion(
                clients=clients,
                active_ai=active_ai,
                config=config,
                system_prompt=system_prompt,
                user_prompt=prompt
            )

            if result_text:
                output_file.write(result_text + "\n")
                print(f"Response received and saved for: {word}")
            
            # Respect rate limits
            time.sleep(1)

    print(f"\nProcess complete. Results saved to: {output_filename}")

if __name__ == "__main__":
    main()