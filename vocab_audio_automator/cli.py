import argparse
from .core import run_pipeline

def main():
    parser = argparse.ArgumentParser(description="Generates Anki Cards with Audio via LLMs.")
    parser.add_argument("csv_file", help="Path to the vocabulary CSV file")
    parser.add_argument("-o", "--output", default="outputs", help="Target directory for generated files (default: 'outputs')")
    parser.add_argument("-n", "--name", default="AI_Generated_Sentences", help="Name of the final .apkg file")
    parser.add_argument("-d", "--deck", default=None, help="Exact Name of the Target Anki Deck (Overrides config)")
    
    args = parser.parse_args()
    
    print(f"--- Starting Anki Generator CLI ---")
    run_pipeline(
        args.csv_file, 
        output_dir=args.output, 
        output_name=args.name, 
        target_deck_name=args.deck,
        status_callback=print
    )

if __name__ == "__main__":
    main()