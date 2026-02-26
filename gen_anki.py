import yaml
import sys
import genanki
import random
import os

#######################################
# Load configuration from config.yaml #
#######################################


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
model_id = config["anki"]["model_id"]
deck_name = config["anki"]["deck_name"]

############################################################################
# Read the list of generated audio files and their corresponding sentences #
############################################################################

with open("outputs/audio/lookup_list.txt", "r", encoding="utf-8") as f:
    audio_files_created = []
    for line in f:
        if line.strip():
            parts = line.strip().split(" | ")
            if len(parts) >= 3:
                audio_files_created.append(
                    {"front": parts[0], "back": parts[1], "audio_file": parts[2]}
                )

##################################
# Create the Anki deck and model #
##################################

print("\n--- Packaging Anki Deck ---")

my_model = genanki.Model(
    model_id,
    deck_name,
    fields=[
        {"name": "Front"},
        {"name": "Back"},
        {"name": "Audio"},
    ],
    templates=[
        {
            "name": "Card 1",
            "qfmt": "{{Front}}<br><br>{{Audio}}",
            "afmt": '{{FrontSide}}<hr id="answer">{{Back}}',
        },
    ],
)

my_deck = genanki.Deck(random.randrange(1 << 30, 1 << 31), deck_name)

media_files_to_export = []

for item in audio_files_created:
    front_text = item["front"]
    back_text = item["back"]
    audio_path = item["audio_file"]

    audio_filename = os.path.basename(audio_path)

    my_note = genanki.Note(
        model=my_model,
        fields=[front_text, back_text, f"[sound:{audio_filename}]"],
    )
    my_deck.add_note(my_note)

    if os.path.exists(audio_path):
        media_files_to_export.append(audio_path)
    else:
        print(f"Warning: File not found: {audio_path}")

print(f"Added {len(media_files_to_export)} notes to the deck.")

output_apkg = "outputs/AI_Generated_Sentences.apkg"
my_package = genanki.Package(my_deck)
my_package.media_files = media_files_to_export

my_package.write_to_file(output_apkg)

print(f"\nSuccess! Your Anki deck is ready: {output_apkg}")
print("Just double-click the file to import it into Anki.")
