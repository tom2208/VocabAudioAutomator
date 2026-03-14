import argparse
from vocab_audio_automator.core.core import run_pipeline
from vocab_audio_automator.utils.strings import CLIStrings


def main():
    parser = argparse.ArgumentParser(description=CLIStrings.MAIN_DESCRIPTION)
    parser.add_argument("input_file", help=CLIStrings.ARG_INPUT_FILE_HELP)
    parser.add_argument(
        "-o",
        "--output",
        default="outputs",
        help=CLIStrings.ARG_OUTPUT_FILE_HELP,
    )
    parser.add_argument(
        "-n",
        "--name",
        default="AI_Generated_Sentences",
        help=CLIStrings.ARG_NAME_HELP,
    )
    parser.add_argument(
        "-d",
        "--deck",
        default=None,
        help=CLIStrings.ARG_DECK_HELP,
    )

    parser.add_argument(
        "-a",
        "--audio-only",
        action="store_true",
        help=CLIStrings.ARG_AUDIO_ONLY_HELP,
    )

    args = parser.parse_args()

    print(CLIStrings.START_INFO)
    run_pipeline(
        args.input_file,
        output_dir=args.output,
        output_name=args.name,
        target_deck_name=args.deck,
        run_audio_only=args.audio_only,
        status_callback=print,
    )


if __name__ == "__main__":
    main()
