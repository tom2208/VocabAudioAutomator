import subprocess
import sys

scripts_to_run = ["gen_sentences.py", "gen_audio.py", "gen_anki.py"]


def main():
    for script in scripts_to_run:
        print(f"Running: {script}...")

        try:
            subprocess.run([sys.executable, script], check=True)

            print(f"Finished: {script}\n")

        except subprocess.CalledProcessError as e:
            print(f"Error: {script} crashed with exit code {e.returncode}.")
            print("Stopping the pipeline to prevent incomplete data.")
            sys.exit(1)
        except FileNotFoundError:
            print(f"Error: Could not find the script '{script}'. Check the spelling.")
            sys.exit(1)


if __name__ == "__main__":
    main()
