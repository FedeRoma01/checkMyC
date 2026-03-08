# C Program Evaluator

## Overview

This project provides an automated evaluation system for C programs, particularly in the context of exam-like assignments. The evaluator integrates **objective metrics** (compilation checks, automated tests, execution performance) with **qualitative analysis** performed by Large Language Models (LLMs).

Given a C program, the corresponding exam description, and evaluation criteria, the system produces a structured evaluation with scores ranging from **0 to 10** and explanatory feedback.

---

## Repository Structure

The repository is organized as follows:

```
project_root/
├── src/
│   └── checkmyc/
│       ├── __main__.py                # Main entry point
│       ├── code/                      # Contains evaluation logic and utilities
│       │   ├── evals.py               # Compilation, timing, and pvcheck logic
│       │   └── config.py              # Program setup functions
|       |
│       ├── api/                       # Contains API logic and utilities
│       │   ├── model_runner.py        # API caller
│       │   ├── gemini_api.py          # Gemini API call
│       │   ├── openrouter_api.py      # Openrouter API call
│       │   ├── openai_api.py          # Openai API call
│       │   └── utils_api.py           # API utility functions
|       |
|       ├── config/                    # Contains .toml configuration files
|       |   ├── llm.toml               # Model pricing and evaluation setup
|       |   └── questions.toml         # Test weights and question configuration
|       |
│       └── data/                      # Static resources
│           ├── prompts/               # Prompts used in API call
│           │   ├──topics/             # Markdown topic descriptions for evaluation (specified in llm.toml)
│           │   ├── system/
│           │   └── user/
|           |
│           └── templates/             # HTML report templates
│
├── resources/
│   ├── sources/                       # C source programs and exam files
|   └── 20220728/                      # exam folder (contains pvcheck.test, context.md, solution.c and input.dat)
|
├── output/                            # Generated output files and reports
│   └── model/                         # output folder containing "model" evaluations
│
├── config.toml                        # General configuration file
├── pyproject.toml                     # Project metadata and dependencies
├── uv.lock                            # Lock file with exact dependency versions for reproducible builds
└── README.md                          # Documentation
```

---

## Features

* **Compilation Check** — evaluates compiler diagnostics, counting warnings and detecting build errors.  
* **Automated Testing** — runs objective checks (`pvcheck`) and performance tests, generating weighted numeric scores for correctness and efficiency.  
* **Performance Measurement** — measures execution time and contributes to the final quantitative assessment.  
* **LLM-based Evaluation** — uses configurable large language models to perform topic-based qualitative analysis of the C program.  
  - Produces detailed evaluations per topic (`score` and `evidences`).
  - Identifies **priority issues** and provides **practical improvement tips**.  
* **Final Scoring** — integrates quantitative test results with LLM-derived evaluations using configurable weighting rules.  
* **Structured Output** — stores all results in a hierarchical JSON structure including:
  - Used model and relative provider.
  - LLM evaluations with per-topic scores, evidences, and criticality levels.  
  - Token usage and cost statistics.  
  - Objective test scores (warnings, performance, pvcheck).  
  - Aggregated scores and weighting parameters used for final computation.
* **HTML file** - visualizes the output in a web page.

---

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/FedeRoma01/checkMyC.git
   cd checkMyC
   ```

2. **Install uv (recommended)**

   `uv` is the recommended tool for dependency management and virtual environments in this project.
   You can install it following the official instructions:

   ```bash
   pip install uv
   ```

   or, if you prefer, use one of the prebuilt binaries from [uv’s installation guide](https://github.com/astral-sh/uv).

3. Set up the environment with **uv**:

   ```bash
   uv sync
   ```

   This will create a `.venv/` virtual environment (excluded from version control) and install all dependencies specified in `pyproject.toml`.

4. Install external tools required for testing:

   * `gcc` (for compilation)
   * [`pvcheck`](https://github.com/claudio-unipv/pvcheck.git) (for automated exam testing)

---

## Usage

### Pre requisites

### LLM Model API Key Requirements

To use LLM models, an API key is required. Three types of keys are supported depending on the chosen model: `openrouter_api_key`, `openai_api_key` and `gemini_api_key`.

- **`openrouter_api_key`**: This key is used when the provider is not explicitly specified. In this case, OpenRouter automatically selects the appropriate provider for the requested model, handling API usage and costs according to the parameters provided in the request.

- **`openai_api_key`**: This key is used when the specified provider is `openai`. API calls are made directly to OpenAI, bypassing OpenRouter, and usage is billed according to OpenAI's pricing.

- **`gemini_api_key`**: This key is used when the specified provider is `gemini`. API calls are made directly to Google, bypassing OpenRouter, and usage is billed according to Google's pricing.

To use them, you have to set it as a environment variable:

**macOS/Linux**:
```bash
export OPENAI_API_KEY="your_api_key_here"
export OPENROUTER_API_KEY="your_api_key_here"
export GOOGLE_API_KEY="your_api_key_here"
```
**Windows**:
```bash
setx OPENAI_API_KEY "your_api_key_here"
setx OPENROUTER_API_KEY "your_api_key_here"
setx GOOGLE_API_KEY "your_api_key_here"
```

### Execute the program

Run the evaluator with:

```bash
uv run checkmyc <program_file.c> <model> [options]
```

### Arguments

* `program` (str): The C program file or the directory containing a set of programs to evaluate.
* `model` (str): LLM model to use.

### Options

* `--exam, -ex` (str): Directory containing exam resources (e.g., exam text, pvcheck test, input for the C program).  
* `--input, -i` (str): Input for the C program.  
* `--context, -cx` (str): Context for the C program.
* `--solution, -sol` (str): Example solution program (used as reference).
* `--config, -cf`: Enables pre-configured input file paths.  
* `--system_prompt, -sp` (str): System prompt file (default: `sp6.md`).  
* `--user_prompt, -up` (str): User prompt file (default: `up4.md`).   
* `--provider, -pr` (str): Provider to use for the specified model. 
* `--prompt_price, -pp` (float): Maximum price per 1M tokens for the prompt (default: '0').  
* `--completion_price, -cp` (float): Maximum price per 1M tokens for the completion (default: '0').
* `--temperature, -t` (int): Temperature to be used in the model (default: 0).
* `--output, -o` (str): Directory in which the final evaluation will be saved.

### Specifications

#### Option `--exam`
When specifying the exam directory, it must contain the following files:

* `pvcheck.test` – Test file for pvcheck.  
* `<my_context>.md` – Context for the C program (e.g., exam text).  
* `<my_input>.dat` – Input file for the C program.
* `<my_solution>.c` - Solution program to be used as reference.

**Notes:**

- The file names `my_context`, `my_input` and `my_solution` are examples; file extensions must be `.md`, `.dat`, `.c`.  
- Using `--exam` automatically ignores `--input`, `--context` and `--solution` options.  
- Recommended when the directory contains context, solution and input files along with `pvcheck.test` to perform the pvcheck test.

#### Option `--provider`
Behavior changes depending on whether a provider is specified:

* **Provider specified**:  
  - The API call will be made **only using that provider** with its default pricing.  

* **Provider not specified**:
  - The API call will attempt multiple providers for the chosen model, starting from the **least expensive**.  
  - Maximum prices set via `--prompt_price` and `--completion_price` will be applied.  

**Note:** Price constraints are only applied when no provider is explicitly specified.

#### Option `--output`
The specified output directory will be put in the directory with the name of the used model. 

### Example

#### Execution with pvcheck

```bash
uv run checkmyc prova.c gpt-4.1-mini -cf -ex 20220728 -up up4.md -sp sp6.md -pr openai
```

This command evaluates `prova.c` against the exam resources in `20220728/` using `gpt-4.1-mini` and specified prompt files. All files refer to pre-configured paths.

#### Execution without pvcheck

```bash
uv run checkmyc prova.c gpt-4.1-mini -cf -i 20220728/Esempio_nel_testo.dat -up up4.md -sp sp6.md
```
This command evaluates `prova.c` without any context and reference solution, using GPT-4.1-mini, `Esempio_nel_testo.dat` as input for `prova.c`, and specified prompt files. All files refer to pre-configured paths.
In this case specifying `-i` is necessary to have a correct performance test, since `prova.c` needs an input file to execute correctly.

---

## Output

Results are saved in the `output_path` specified in `config.toml`, organized by model type (`<model>/`).
Each evaluation produces two output files with identical base names but different extensions:
* `<timestamp>_<program>_<systemPrompt>_<userPrompt>_<schema>.json`
* `<timestamp>_<program>_<systemPrompt>_<userPrompt>_<schema>.html`

Each output JSON file includes the following sections, while the corresponding HTML file renders the results in a human-readable format using a predefined Jinja2 template (`report_template.html`), allowing quick visualization of the evaluation outcome:

### **LLM**
Contains the model’s qualitative evaluation of the C program:

- **`evaluations`** — list of evaluated topics. Each topic includes:
  - **`name`**: the concept evaluated (e.g., *Control structures*, *Functions*).
  - **`score`**: numeric score from 0 to 10.
  - **`evidences`** — list of observations with:
    - **`comment`**: textual explanation of the issue or observation.
    - **`lines`**: list of line ranges in the source code (e.g., `"51-55"`, `"118-171"`).
    - **`goodness`**: goodness indication of the related comment (`"+"` or `"-"`).
    - **`criticality`**: qualitative severity level (`"high"`, `"medium"`, `"low"`).
- **`priority issues`** — concise list of the most severe problems detected.
- **`practical_tips`** — prioritized suggestions for fixing or improving the code.

### **usage**
Information about model usage and cost:
- `input_tokens`, `output_tokens`, `cached_tokens` and `total_tokens` indicate the number of tokens processed.
- `call_cost` gives the estimated monetary cost of the model call.

### **tests_scores**
Objective evaluation metrics:
- **`warning`** — compilation quality based on compiler diagnostics.
- **`performance`** — runtime efficiency evaluation.
- **`pvcheck`** — correctness of program behavior against expected outputs.
- **`final`** — combined test score.

### **llm_scores**
Aggregated scores per topic and their weighted average:
- Each key corresponds to a topic (e.g., *Pointers*, *File handling*).
- The `final` field represents the weighted LLM-based score.

### **final_score**
Overall combined score derived from LLM evaluation and objective tests.

### **weights**
Weighting coefficients used for score aggregation:
- `pvcheck_questions`, `tests`, and `llm` define how partial scores contribute to the total.
- The `final` section specifies the relative influence of LLM and test scores.


---

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.
