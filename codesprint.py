# # CodeSprint AI: Multi-Model Python Performance Optimizer
#
# Paste slow Python → fan out to multiple LLMs → translate to C++ or Rust → compile, run, validate output, report speedup.
#
# Extends the Week 4 lab with:
# 1. Rust as a second target language
# 2. Multi-model fan-out in one click
# 3. Output validation (exact + numeric tolerance)
# 4. A leaderboard table in the UI

# %%
# Imports

import os, io, sys, time, subprocess, re
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr

# %%
# Load environment variables from .env file
load_dotenv(override=True)

openai     = OpenAI()
anthropic  = OpenAI(api_key=os.getenv('ANTHROPIC_API_KEY'),  base_url="https://api.anthropic.com/v1/")
gemini     = OpenAI(api_key=os.getenv('GOOGLE_API_KEY'),     base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
grok       = OpenAI(api_key=os.getenv('GROK_API_KEY'),       base_url="https://api.x.ai/v1")
groq       = OpenAI(api_key=os.getenv('GROQ_API_KEY'),       base_url="https://api.groq.com/openai/v1")
openrouter = OpenAI(api_key=os.getenv('OPENROUTER_API_KEY'), base_url="https://openrouter.ai/api/v1")

# Define the models and their corresponding clients
models = [
    "gpt-5",
    "claude-sonnet-4-5-20250929",
    "gemini-2.5-pro",
    "grok-4",
    "openai/gpt-oss-120b",
    "qwen/qwen3-coder-30b-a3b-instruct",
]

clients = {
    "gpt-5": openai,
    "claude-sonnet-4-5-20250929": anthropic,
    "gemini-2.5-pro": gemini,
    "grok-4": grok,
    "openai/gpt-oss-120b": groq,
    "qwen/qwen3-coder-30b-a3b-instruct": openrouter,
}

# %%
# C++ : compile commands and run commands
cpp_compile  = ["clang++", "-std=c++17", "-O3", "-DNDEBUG", "main.cpp", "-o", "main_cpp"]
cpp_run      = ["./main_cpp"]

# Rust — compile commands and run commands
rust_compile = ["rustc", "--edition", "2021", "-O", "main.rs", "-o", "main_rs"]
rust_run     = ["./main_rs"]

# %%
# System and User Prompts

def system_prompt(target):
    lang = "C++17" if target == "cpp" else "Rust (edition 2021, no external crates)"
    return f"""Convert Python to {lang} that produces byte-identical stdout and runs as fast as possible.
Respond with code only - no markdown fences, no explanation."""

def user_prompt(python, target):
    return f""" Port the following Python code to {'C++' if target == "cpp" else "Rust"}. Match stdout exactly (formatting, decimals, newlines). Single self-contained file. Stdlib only.

```python
{python}
```"""


# Generate messages for the LLMs
def messages_for_llms(python, target):
    return [
        {"role": "system", "content": system_prompt(target)},
        {"role": "user",   "content": user_prompt(python, target)},
    ]

# %%
# Write the generated code to a file
def write_source(code, target):
    filename = "main.cpp" if target == "cpp" else "main.rs"
    with open(filename, "w") as f:
        f.write(code)

# Translate the Python code to the target language using the specified model
def translate(model, python, target):
    client = clients[model]
    reasoning_effort = "high" if "gpt" in model else None
    t0 = time.perf_counter()
    resp = client.chat.completions.create(
        model=model,
        messages=messages_for_llms(python, target),
        reasoning_effort=reasoning_effort,
    )
    elapsed = time.perf_counter() - t0
    code = resp.choices[0].message.content
    for fence in ["```cpp", "```rust", "```"]:
        code = code.replace(fence, "")
    code = code.strip()
    write_source(code, target)
    return code, elapsed

# %%
# Compile and run the generated code, capturing stdout, stderr, and execution time

def compile_and_run(target):
    compile_cmd, run_cmd = (cpp_compile, cpp_run) if target == "cpp" else (rust_compile, rust_run)
    try:
        subprocess.run(compile_cmd, check=True, text=True, capture_output=True, timeout=30)
    except FileNotFoundError:
        return None, f"COMPILER NOT FOUND: {compile_cmd[0]}", 0.0
    except subprocess.CalledProcessError as e:
        return None, f"COMPILE ERROR:\n{e.stderr}", 0.0
    except subprocess.TimeoutExpired:
        return None, "COMPILE TIMEOUT (>30s)", 0.0

    t0 = time.perf_counter()
    try:
        out = subprocess.run(run_cmd, check=True, text=True, capture_output=True, timeout=15)
    except FileNotFoundError:
        return None, f"EXECUTABLE NOT FOUND: {run_cmd[0]}", time.perf_counter() - t0
    except subprocess.CalledProcessError as e:
        return None, f"RUN ERROR:\n{e.stderr}", time.perf_counter() - t0
    except subprocess.TimeoutExpired:
        return None, "RUN TIMEOUT (>15s)", time.perf_counter() - t0
    return out.stdout, "", time.perf_counter() - t0

# %%
# Compile and run the original Python code, capturing stdout, stderr, and execution time

def run_python(code):
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    t0 = time.perf_counter()
    try:
        exec(code, {"__builtins__": __builtins__})
    except Exception as e:
        sys.stdout = old
        return None, f"PYTHON ERROR: {e}", 0.0
    sys.stdout = old
    return buf.getvalue(), "", time.perf_counter() - t0

NUMERIC_RE = re.compile(r"-?\d+\.?\d*(?:[eE][-+]?\d+)?")

def validate(ref, candidate, tol=1e-6):
    """Return (matches: bool, mode: str)."""
    r = "\n".join(l.rstrip() for l in ref.splitlines()).rstrip()
    c = "\n".join(l.rstrip() for l in candidate.splitlines()).rstrip()
    if r == c:
        return True, "exact"
    rt, ct = r.split(), c.split()
    if len(rt) == len(ct) and all(NUMERIC_RE.fullmatch(x) for x in rt[:5] or [""]):
        try:
            if all(abs(float(x) - float(y)) <= tol for x, y in zip(rt, ct)):
                return True, f"numeric (tol={tol})"
        except ValueError:
            pass
    return False, "mismatch"

# %%
# Sample Python code to be translated and benchmarked

pi = """
import time
def calculate(iterations, p1, p2):
    result = 1.0
    for i in range(1, iterations+1):
        result -= 1/(i*p1 - p2)
        result += 1/(i*p1 + p2)
    return result
start = time.time()
print(f"Result: {calculate(50_000_000, 4, 1)*4:.12f}")
print(f"Elapsed: {time.time()-start:.6f}s")
"""

ref_out, _, ref_time = run_python(pi)
print("Python ref:", ref_time, "s")
print(ref_out)

# %%
# ## Gradio UI
#
# Pick a Python program, a target language, and one or more models. The app fans out, compiles each translation, validates output, and shows the leaderboard.

# %%
def run_benchmark(python_code, target, selected_models):
    if not selected_models:
        return [["(pick at least one model)"]], "", ""

    ref_out, ref_err, ref_time = run_python(python_code)
    if ref_out is None:
        return [[ref_err]], "", ""

    header = ["Model", "Translate (s)", "Native (s)", "Speedup", "Output", "Notes"]
    rows = [header]
    code_dump = []

    for model in selected_models:
        try:
            code, t_translate = translate(model, python_code, target)
        except Exception as e:
            rows.append([model, "—", "—", "—", "—", f"translate err: {e}"[:80]])
            continue

        cand_out, err, t_run = compile_and_run(target)
        if cand_out is None:
            rows.append([model, f"{t_translate:.2f}", "—", "—", "fail", err.splitlines()[0][:80]])
            code_dump.append(f"### {model}\n```{target}\n{code}\n```")
            continue

        ok, mode = validate(ref_out, cand_out)
        speedup = f"{ref_time / t_run:.1f}x" if t_run > 0 else "—"
        rows.append([model, f"{t_translate:.2f}", f"{t_run:.4f}", speedup, "match" if ok else "diff", mode])
        code_dump.append(f"### {model}\n```{target}\n{code}\n```")

    summary = f"Python reference: {ref_time:.4f}s\n```\n{ref_out}```"
    return rows, summary, "\n\n".join(code_dump)

with gr.Blocks(title="CodeSprint AI") as ui:
    gr.Markdown("# CodeSprint AI\nMulti-model Python → C++/Rust optimizer with output validation.")
    with gr.Row():
        with gr.Column():
            code_in = gr.Code(value=pi, language="python", label="Python input", lines=18)
            target  = gr.Radio(["cpp", "rust"], value="cpp", label="Target")
            picked  = gr.CheckboxGroup(models, value=models[:2], label="Models")
            run_btn = gr.Button("Run benchmark", variant="primary")
        with gr.Column():
            tbl     = gr.Dataframe(label="Leaderboard", wrap=True)
            ref_md  = gr.Markdown(label="Python reference")
            code_md = gr.Markdown(label="Generated code")
    run_btn.click(run_benchmark, [code_in, target, picked], [tbl, ref_md, code_md])

ui.launch(inbrowser=True)
