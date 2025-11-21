import csv
import io
import logging
import platform
import shutil
import subprocess
import time
from pathlib import Path


def add_line_numbers(code: str) -> str:
    """Add line numbers for relative comments in the output."""
    lines = []
    for i, line in enumerate(code.splitlines(), start=1):
        lines.append(f"{i:4d} | {line}")

    return "".join(lines)


def get_exec_name() -> str:
    """Return the default executable name depending on platform."""
    return "a.exe" if platform.system() == "Windows" else "a.out"


def compilation_test(file_path: str) -> float:
    """Compile C code with GCC and compute a warning-based score."""
    if not shutil.which("gcc"):
        logging.error("gcc not found")
        return -1

    compile_cmd = ["gcc", "-Wall", "-Wextra", file_path]
    try:
        result = subprocess.run(compile_cmd, capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            logging.info("Compilation error")
            return 0

        warnings = result.stderr.count("warning:")
        score = float(max(0, 10 - warnings))
        return float(score)
    except subprocess.TimeoutExpired:
        logging.info("Compilation timed out")
        return 0


def time_test(p_input) -> float:
    """Run compiled program and assign a score based on runtime."""
    exec_name = get_exec_name()
    exec_path = Path(exec_name)
    if not exec_path.exists():
        logging.error(f"Executable {exec_name} not found")
        return -1

    if not Path(p_input).exists():
        logging.error(f"Input file {p_input} not found")
        return -1

    run_cmd = [f"./{exec_name}", str(p_input)]
    res = 0
    try:
        start = time.perf_counter()
        result = subprocess.run(run_cmd, capture_output=True, timeout=5)
        elapsed = time.perf_counter() - start

        if result.returncode != 0:
            logging.info(f"Program crashed or returned error {result.returncode}")
            return 0

        else:
            if elapsed < 1:
                res = 10
            elif elapsed < 2:
                res = 8
            else:
                res = 6
    except subprocess.TimeoutExpired:
        logging.info("Execution timed out")

    return float(res)


def pvcheck_test(
    pvcheck_weights: dict, pvcheck_csv_scores: dict, exam_dir_path: str
) -> float:
    """Run pvcheck tool and compute weighted normalized score."""
    if not shutil.which("pvcheck"):
        logging.error("pvcheck not found")
        return -1

    exec_name = get_exec_name()
    pv_file = Path(exam_dir_path) / "pvcheck.test"
    if not pv_file.exists():
        logging.error(f"pvcheck.test not found in {exam_dir_path}")
        return -1
    pvcheck_cmd = ["pvcheck", "-F", "csv", "-f", str(pv_file), f"./{exec_name}"]
    try:
        result = subprocess.run(pvcheck_cmd, capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            logging.warning(f"pvcheck exited with code {result.returncode}")

        reader = csv.DictReader(io.StringIO(result.stdout))
        for row in reader:
            for k, v in row.items():
                pvcheck_csv_scores[k].append(v)

        # Extract and normalize scores
        scores_list = [float(v[-1]) for k, v in list(pvcheck_csv_scores.items())[2:]]
        norm_scores = [s / 10 for s in scores_list]

        weights_list = list(pvcheck_weights.values())
        total_weights = sum(weights_list)
        if not total_weights:
            return 0
        norm_weights = [w / total_weights for w in weights_list]
        return sum(v * w for v, w in zip(norm_scores, norm_weights, strict=False))
    except subprocess.TimeoutExpired:
        logging.info("pvcheck execution timed out")
        return 0


def compute_final_score(
    objective_metrics: dict,
    llm_metrics: dict,
    tests_weights: dict,
    llm_weights: dict,
    combined_weights: dict,
    quest_weights: dict,
    pvcheck_csv_scores: dict,
) -> dict:
    """Compute combined final score from objective and LLM metrics."""
    valid_tests = {t: v for t, v in objective_metrics.items() if v != -1.0}
    if valid_tests:
        weighted_sum = sum(tests_weights[t] * v for t, v in valid_tests.items())
        total_weight = sum(tests_weights[t] for t in valid_tests)
        tests_score = weighted_sum / total_weight
    else:
        tests_score = 0  # no tests executed

    for t, v in objective_metrics.items():
        if v == -1:
            objective_metrics[t] = "Not executed"
            tests_weights[t] = "Not considered"

    # LLM score
    llm_metrics_spec = {arg["name"]: arg["score"] for arg in llm_metrics["evaluations"]}
    llm_sum = sum(
        arg["score"] * llm_weights[arg["name"]] for arg in llm_metrics["evaluations"]
    )
    llm_score = llm_sum / sum(llm_weights.values())

    # Final score
    total_combined_weights = sum(combined_weights.values())
    final_score = (
        combined_weights["tests"] * tests_score + combined_weights["llm"] * llm_score
    ) / total_combined_weights

    pv_data = {
        k: [(float(x) if x != "MISS" else 0) for x in v]
        for k, v in list(pvcheck_csv_scores.items())[2:]
    }

    return {
        "pvcheck": pv_data,
        "tests_scores": {**objective_metrics, "final": tests_score},
        "llm_scores": {**llm_metrics_spec, "final": llm_score},
        "final_score": final_score,
        "weights": {
            "pvcheck_questions": quest_weights,
            "tests": tests_weights,
            "llm": llm_weights,
            "final": combined_weights,
        },
    }
