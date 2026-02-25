from utils import get_data_from_output
import yaml
import sys
from openai import OpenAI
import random
import os
import time
import base64
import edge_tts
import asyncio
from dotenv import load_dotenv

look_up_list = []

results = get_data_from_output("outputs")


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
api_key = os.getenv("OPENAI_API_KEY")
model_id = config["openai"]["model_id"]
chatgpt_mini_voices = config["openai"]["voices"]
edge_tts_voices = config["edge_tts"]["voices"]
speed = config["openai"]["speed"]
target_language = config["defaults"]["target_language"]
audio_instructions = config["prompts"]["audio_instructions"]
audio_model = config["model"]["audio"]

if audio_model == "openai":
    if not api_key:
        raise ValueError("Missing OpenAI API key! Please check your .env file.")
    client = OpenAI(api_key=api_key, base_url="https://api.openai.com/v1")

audio_folder = "outputs/audio"
os.makedirs(audio_folder, exist_ok=True)


def gen_unique_filename(base_name="audio", extension=".mp3"):
    timestamp = int(time.time() * 1000)
    return f"{base_name}_{timestamp}{extension}"


def generate_audio_edge(text, filename):
    """
    Generates free, highly accurate TTS using Microsoft Edge's neural voices.
    """

    voice = random.choice(edge_tts_voices)

    async def _generate():
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(filename)

    look_up_list.append((target, source, filename, voice))
    asyncio.run(_generate())


def generate_audio_gpt4o(text, filename):
    voice = random.choice(chatgpt_mini_voices)
    response = client.chat.completions.create(
        model=model_id,
        modalities=["text", "audio"],  # We tell it we want audio back
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

    look_up_list.append((target, source, filename, voice))
    with open(filename, "wb") as f:
        f.write(base64.b64decode(audio_data_b64))


print(f"Generating audio for {len(results)} sentences using model '{audio_model}'...")

for target, source in results:
    file_name = gen_unique_filename(base_name=target_language.replace(" ", "_"))
    unique_filename = gen_unique_filename(file_name)
    file_path = os.path.join(audio_folder, unique_filename)
    print(
        f"({len(look_up_list)+1}/{len(results)}) Generating audio for: '{target}' with filename: '{file_name}'"
    )
    if audio_model == "openai":
        generate_audio_gpt4o(target, file_path)
    elif audio_model == "edge_tts":
        generate_audio_edge(target, file_path)
    else:
        print(
            f"Error: Unsupported audio model '{audio_model}' specified in config.yaml."
        )
        sys.exit(1)
    print(f"Audio generated and saved at '{file_name}'")

with open("outputs/audio/lookup_list.txt", "w", encoding="utf-8") as f:
    for target, source, audio_path, voice in look_up_list:
        f.write(f"{target} | {source} | {audio_path} | {voice}\n")

print(
    "Audio generation complete. Lookup list saved to 'outputs/audio/lookup_list.txt'."
)
