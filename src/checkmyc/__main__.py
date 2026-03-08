import argparse
import json
import logging
import re
import sys
import tomllib
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from time import sleep

from .api.model_runner import get_provider
from .api.utils_api import (
    CacheAPIError,
    FatalAPIError,
    TransientAPIError,
    compute_cost,
    save_debug_pair,
)
from .code.config import (
    build_prompt_context,
    cons_lines_to_list,
    generate_schema,
    get_paths,
    load_exam_context,
    load_file,
    programs_loading,
    render_prompts,
    save_json_and_html,
)
from .code.evals import (
    add_line_numbers,
    compilation_test,
    compute_final_score,
    generate_topic_score,
    pvcheck_test,
    time_test,
)


class APIError(Exception):
    """Base class for all API-related errors."""

    pass


class InvalidResponseError(APIError):
    """Raised when the model response is invalid or empty."""

    pass


# Project layout helpers (resolve absolute dirs independent from cwd)
PROJECT_ROOT = Path(__file__).resolve().parents[2]  # repo root
PKG_ROOT = Path(__file__).resolve().parents[0]  # src/checkmyc
DATA_DIR = PKG_ROOT / "data"
TEMPLATES_DIR = DATA_DIR / "templates"


def init_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluates a given C program")
    parser.add_argument("program", type=str, help="C program file to evaluate")
    parser.add_argument("model", type=str, help="Model to use for evaluation")
    parser.add_argument("--input", "-i", type=str, help="Input file for the C program")
    parser.add_argument(
        "--context", "-cx", type=str, help="File containing program context"
    )
    parser.add_argument(
        "--solution", "-sol", type=str, help="File containing example solution program"
    )
    parser.add_argument(
        "--exam", "-ex", type=str, help="Directory containing program context resources"
    )
    parser.add_argument(
        "--config",
        "-cf",
        action="store_true",
        help="Use preconfigured paths from config.toml",
    )
    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        help="Activate debug prints",
    )
    parser.add_argument(
        "--user_prompt",
        "-up",
        type=str,
        default="no_context.md",
        help="User prompts file",
    )
    parser.add_argument(
        "--system_prompt",
        "-sp",
        type=str,
        default="no_context.md",
        help="System prompts file",
    )
    parser.add_argument(
        "--provider", "-pr", type=str, help="Provider (openai/gemini/openrouter)"
    )
    parser.add_argument(
        "--prompt_price",
        "-pp",
        type=float,
        default=0.000001,
        help="Max price per 1M prompt tokens",
    )
    parser.add_argument(
        "--completion_price",
        "-cp",
        type=float,
        default=0.000001,
        help="Max price per 1M completion tokens",
    )
    parser.add_argument(
        "--temperature", "-t", type=float, default=0.3, help="Model temperature"
    )
    parser.add_argument("--output", "-o", type=str, help="Output directory for results")
    parser.add_argument(
        "--output_directory",
        "-od",
        type=str,
        help="Output directory inside the model dir",
    )
    return parser


def make_safe_dirname(s: str) -> str:
    safe_name = re.sub(r"[^a-zA-Z0-9-_]", "_", s)
    safe_name = re.sub(r"_+", "_", safe_name)
    safe_name = safe_name.strip("_")
    return safe_name


logging.basicConfig(level=logging.ERROR, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def main():
    parser = init_argparser()
    input_args = parser.parse_args()
    debug = input_args.debug
    path_flag = input_args.config

    # CONFIGURATION LOAD
    config_path = PROJECT_ROOT / "config.toml"
    if not config_path.exists():
        raise FileNotFoundError(
            f"config.toml not found at expected location: {config_path}"
        )
    with config_path.open("rb") as f:
        general_config = tomllib.load(f)

    paths = get_paths(general_config, path_flag, input_args)
    combined_weights = general_config.get("combined_weights", {})

    # LLM CONFIG LOAD
    llm_config_path = paths.get("llm_config")
    if not llm_config_path:
        raise FileNotFoundError("llm_config path missing in config.toml")
    with open(llm_config_path, "rb") as f:
        llm_config = tomllib.load(f)
    topics = llm_config["topics"]
    llm_weights = {a["name"]: a["weight"] for a in topics}
    pricing = llm_config.get("models", {})
    comments_weights = llm_config.get("weights", {})

    # QUESTIONS CONFIG LOAD
    questions_config_path = paths.get("questions_config")
    if not questions_config_path:
        raise FileNotFoundError("questions_config path missing in config.toml")
    with open(questions_config_path, "rb") as f:
        questions = tomllib.load(f)
    tests_weights = questions["tests_weights"]
    tests = list(tests_weights.keys())

    # PROGRAM LOAD (prepare list of program file Paths)
    program_paths = programs_loading(paths, ".c")

    # EXAM/CONTEXT & SOLUTION HANDLING
    exam_dir, exam_ctx = load_exam_context(input_args, paths, questions)

    # SCHEMA
    topic_list = [t["name"] for t in topics]
    schema = generate_schema(topic_list)

    # PROMPTS CONSTRUCTION
    args_md = build_prompt_context(topics, paths.get("topics_path"))
    sys_prompt_path = paths.get("sys_prompt")
    usr_prompt_path = paths.get("usr_prompt")
    if not sys_prompt_path or not Path(sys_prompt_path).exists():
        raise FileNotFoundError(f"System prompt not found: {sys_prompt_path}")
    if not usr_prompt_path or not Path(usr_prompt_path).exists():
        raise FileNotFoundError(f"User prompt not found: {usr_prompt_path}")

    system_prompt_name = Path(sys_prompt_path).stem
    user_prompt_name = Path(usr_prompt_path).stem

    provider_name = input_args.provider
    model = input_args.model
    temperature = input_args.temperature
    provider = get_provider(provider_name)

    for program_path in program_paths:
        program_name = Path(program_path).name
        abs_program_path = "file://" + str(Path(program_path).resolve())
        program_info = {
            "name": program_name,
            "path": abs_program_path,
            "to_visual_path": str(program_path),
        }
        program_text = add_line_numbers(load_file(program_path))

        # OBJECTIVE TESTS
        metrics = dict.fromkeys(tests, -1.0)
        metrics[tests[0]] = compilation_test(str(program_path))
        metrics[tests[1]] = time_test(exam_ctx.program_input)
        pvcheck_csv_scores = defaultdict(list)
        if exam_dir and exam_ctx.pvcheck_flag:
            metrics[tests[2]] = pvcheck_test(
                questions["questions_weights"],
                pvcheck_csv_scores,
                str(exam_ctx.exam_path),
            )

        # PROMPT COMPILING
        templ_context = {
            "schema_flag": False,
            "schema": schema,
            "topics": args_md,
            "context": exam_ctx.context,
            "solution": exam_ctx.solution,
            "program": program_text,
        }

        system_prompt, user_prompt = render_prompts(
            str(sys_prompt_path), str(usr_prompt_path), templ_context
        )

        # Debug saving of system and user prompts used
        if debug:
            with open(
                PROJECT_ROOT / "rendered_prompts" / "system_prompt.md",
                "w",
                encoding="utf-8",
            ) as f:
                f.write(system_prompt)
            with open(
                PROJECT_ROOT / "rendered_prompts" / "user_prompt.md",
                "w",
                encoding="utf-8",
            ) as f:
                f.write(user_prompt)

        # API CALL
        max_retries = 2
        skip_prog = False
        for attempt in range(max_retries + 1):
            try:
                out_text, out_usage = provider.run(
                    system_prompt, user_prompt, schema, model, temperature
                )
                if debug:
                    save_debug_pair(out_text, out_usage.model_dump(), "debugs")
                parsed = json.loads(out_text)
                usage = out_usage.model_dump() if out_usage else {}
                # no exception -> no retry needed
                break
            except CacheAPIError as e:
                logger.error(f"[CACHE] {e}")
                skip_prog = True
            except TransientAPIError as e:
                if attempt == max_retries:
                    logger.error(f"[TRANSIENT] Retry logic didn't work: {e}")
                    skip_prog = True
                else:
                    print(f"Retrying API call for {program_name}")
                    sleep(2**attempt)
            except FatalAPIError as e:
                logger.error(f"[FATAL] API error: {e}")
                skip_prog = True
                break
            except json.JSONDecodeError as e:
                save_debug_pair(out_text, out_usage, "failures")
                logger.error(
                    f"Invalid JSON in response (see debug files in logs/failures): {e}"
                )
                skip_prog = True

        if skip_prog:
            print(f"API call for {program_name} FAILED")
            continue  # skip the rest of the external iteration
        # other instructions are executed if the API call was successful

        tokens = provider.normalize_usage(usage)
        call_cost = compute_cost(model, tokens, pricing)

        # CONSECUTIVE LINES CONTROL
        for topic in parsed["evaluations"]:
            for comment in topic["evidences"]:
                comment["lines"] = cons_lines_to_list(comment["lines"])

        # DETERMINISTIC SCORE GENERATION FROM EVIDENCES
        generate_topic_score(parsed["evaluations"], comments_weights)

        # FINAL SCORE
        combined = compute_final_score(
            metrics,
            parsed,
            comments_weights,
            tests_weights,
            llm_weights,
            combined_weights,
            exam_ctx.quest_weights,
            pvcheck_csv_scores,
        )

        # SAVE OUTPUT path
        timestamp = datetime.now().strftime("%H-%M-%S")
        output_dir = (
            Path(paths.get("output"))
            / make_safe_dirname(model)
            / (input_args.output_directory or "")
        )
        output_dir.mkdir(parents=True, exist_ok=True)
        output_name = (
            f"{timestamp}_{program_name}_{system_prompt_name}_{user_prompt_name}.json"
        )
        output_path = output_dir / output_name

        save_json_and_html(
            program_info,
            output_path,
            parsed,
            model,
            provider_name,
            tokens,
            call_cost,
            combined,
        )


if __name__ == "__main__":
    try:
        main()
    except (APIError, InvalidResponseError, OSError) as e:
        logger.error(f"API or system error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Unexpected fatal error: {e}")
        sys.exit(1)
