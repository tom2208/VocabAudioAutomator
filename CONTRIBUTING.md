# Contributing to VocabAudioAutomator

First off, thanks for taking the time to contribute! ❤️

## 🛠️ Development Setup

1. Clone the repo and install dependencies:
   ```bash
   git clone [https://github.com/tom2208/VocabAudioAutomator.git](https://github.com/tom2208/VocabAudioAutomator.git)
   cd VocabAudioAutomator
   poetry install
   ```

## 🎨 Code Formatting (Black)

This project strictly follows the **[Black](https://black.readthedocs.io/en/stable/)** code formatting style. Our GitHub Actions CI pipeline will automatically check your code formatting and will reject any Pull Requests that don't meet the standard.

Before committing your changes, please run the formatter in the root directory of the project:

```bash
poetry run black .
```

## 🚀 Pull Request Process

1. Create a new branch for your feature (`git checkout -b feature/AmazingFeature`).
2. Make your changes and make sure to format them with `black`.
3. Push your branch and open a Pull Request against the `main` branch.