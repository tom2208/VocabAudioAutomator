from pathlib import Path


def get_data_from_output(directory_name="output"):
    print(f"Reading all txt data from directory: {directory_name}")

    results = []
    output_path = Path(directory_name)

    if not output_path.is_dir():
        print(f"Error: The directory '{directory_name}' was not found.")
        return results

    for file_path in output_path.glob("*.txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                clean_line = line.strip()
                if "|" in clean_line:
                    target, source = clean_line.split("|", 1)
                    results.append((target.strip(), source.strip()))

    return results
