# CodeSprint AI

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-API-412991?style=for-the-badge&logo=openai&logoColor=white)
![Gradio](https://img.shields.io/badge/Gradio-UI-F97316?style=for-the-badge)
![C++17](https://img.shields.io/badge/C%2B%2B-17-00599C?style=for-the-badge&logo=cplusplus&logoColor=white)
![Rust](https://img.shields.io/badge/Rust-2021-000000?style=for-the-badge&logo=rust&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626?style=for-the-badge&logo=jupyter&logoColor=white)

CodeSprint AI is a multi-model Python performance optimizer. It takes Python code, sends it to multiple LLM providers, translates it into optimized C++17 or Rust 2021, compiles the generated program, runs it, validates stdout, and reports speedups in a Gradio leaderboard.

## Preview

The app provides an interactive benchmark workflow:

![CodeSprint AI app preview](assets/codesprint-ai-preview.png)

## Features

- Multi-provider LLM routing through OpenAI-compatible clients.
- Python to C++17 and Rust 2021 code generation.
- Native compilation and runtime benchmarking.
- Exact stdout validation with numeric tolerance fallback.
- Gradio interface with model selection and leaderboard output.
- Notebook workflow plus exported Python script for easier portfolio review.

## Skills Demonstrated

![LLM Engineering](https://img.shields.io/badge/LLM%20Engineering-111827?style=flat-square)
![Prompt Engineering](https://img.shields.io/badge/Prompt%20Engineering-2563EB?style=flat-square)
![Python Automation](https://img.shields.io/badge/Python%20Automation-3776AB?style=flat-square)
![API Integration](https://img.shields.io/badge/API%20Integration-059669?style=flat-square)
![Benchmarking](https://img.shields.io/badge/Benchmarking-DC2626?style=flat-square)
![Compiler Tooling](https://img.shields.io/badge/Compiler%20Tooling-7C3AED?style=flat-square)
![Gradio Apps](https://img.shields.io/badge/Gradio%20Apps-F97316?style=flat-square)
![C++](https://img.shields.io/badge/C%2B%2B%20Optimization-00599C?style=flat-square)
![Rust](https://img.shields.io/badge/Rust%20Optimization-000000?style=flat-square)
![Jupyter](https://img.shields.io/badge/Jupyter%20Prototyping-F37626?style=flat-square)

## Tech Stack

- Python 3.12
- Jupyter Notebook
- Gradio
- OpenAI Python SDK
- OpenAI-compatible APIs for Anthropic, Gemini, Grok, Groq, and OpenRouter
- C++17 compiler via `clang++`
- Rust compiler via `rustc`

## Project Files

- `codesprint.ipynb`: main notebook version of the app.
- `codesprint.py`: Python script exported from the notebook.
- `.env.cloud`: placeholder cloud environment template.
- `.gitignore`: ignores local secrets and virtual environments.

## Setup

Create and activate a virtual environment:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install ipykernel python-dotenv openai gradio
```

Add real API keys to `.env`:

```bash
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
GOOGLE_API_KEY=your-google-key
GROK_API_KEY=your-grok-key
GROQ_API_KEY=your-groq-key
OPENROUTER_API_KEY=your-openrouter-key
```

Run the Python app:

```bash
python codesprint.py
```

Or open `codesprint.ipynb` in Jupyter or VS Code and run the cells.

## Compiler Notes

C++ mode requires `clang++`.

Rust mode requires `rustc`:

```bash
brew install rust
```

If a compiler is missing, the app reports a readable error such as `COMPILER NOT FOUND: rustc`.

## Portfolio Highlights

This project shows practical AI engineering beyond a simple chat wrapper: provider routing, prompt design, generated code cleanup, compiler orchestration, runtime measurement, and correctness validation all inside one usable interface.
