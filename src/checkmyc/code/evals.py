import csv
import io
import logging
import platform
import shutil
import subprocess
import time
from collections import Counter
from pathlib import Path


def add_line_numbers(code: str) -> str:
    """Add line numbers for relative comments in the output."""
    code = code.expandtabs(4)
    lines = []
    for i, line in enumerate(code.splitlines(), start=1):
        lines.append(f"{i:4d} | {line}")

    return "\n".join(lines)


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
        result = subprocess.run(compile_cmd, capture_output=True, text=True, timeout=5)
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


def generate_topic_score(
    topic_evals,
    rules_map,
    topic_comments_weights,
    start_score=10,
    min_score=0,
    max_score=10,
):
    """Enriches evidence with goodness/criticality from the rules_map
    and calculates the weighted score."""
    mapping = {"+": "plus", "-": "minus"}

    for topic in topic_evals:
        t_name = topic.get("topic_name")
        topic_rules = rules_map.get(t_name, {})
        current_weights = topic_comments_weights.get(t_name, {})

        for ev in topic["evidences"]:
            try:
                c_id = int(ev["condition_id"])
                rule_info = topic_rules.get(c_id, {})
            except (ValueError, TypeError):
                rule_info = {}

            ev["goodness"] = rule_info.get("goodness", "=")
            ev["criticality"] = rule_info.get("criticality", "neutral")

        seen_ids = set()
        unique_metadata = []

        for ev in topic["evidences"]:
            c_id = ev["condition_id"]
            if c_id not in seen_ids:
                unique_metadata.append((ev["goodness"], ev["criticality"]))
                seen_ids.add(c_id)

        counts = Counter(unique_metadata)

        adjustment = 0
        for (good, crit), freq in counts.items():
            if good == "=" or crit == "neutral":
                continue
            good_key = mapping.get(good)
            weight = current_weights[crit][good_key]
            adjustment += weight * freq

        weighted_score = start_score + adjustment
        topic["weighted_score"] = max(
            min_score, min(max_score, round(weighted_score, 2))
        )


def compute_final_score(
    objective_metrics: dict,
    llm_metrics: dict,
    comments_weights: dict,
    tests_weights: dict,
    llm_weights: dict,
    combined_weights: dict,
    quest_weights: dict,
    pvcheck_csv_scores: dict,
) -> dict:
    """Compute combined final score from objective and LLM metrics."""
    valid_test_keys = [t for t, v in objective_metrics.items() if v != -1.0]

    if valid_test_keys:
        weighted_sum = sum(
            float(tests_weights[t]) * float(objective_metrics[t])
            for t in valid_test_keys
        )
        total_weight = sum(float(tests_weights[t]) for t in valid_test_keys)
        tests_score = weighted_sum / total_weight if total_weight > 0 else 0
    else:
        tests_score = 0

    report_metrics = objective_metrics.copy()
    report_weights = tests_weights.copy()

    for t in objective_metrics:
        if objective_metrics[t] == -1:
            report_metrics[t] = "Not executed"
            report_weights[t] = "Not considered"

    # LLM score
    llm_metrics_spec = {
        arg["topic_name"]: arg["weighted_score"] for arg in llm_metrics["evaluations"]
    }

    total_llm_weight = sum(llm_weights.values())
    llm_sum = sum(
        arg["weighted_score"] * llm_weights[arg["topic_name"]]
        for arg in llm_metrics["evaluations"]
    )
    llm_score = llm_sum / total_llm_weight if total_llm_weight > 0 else 0

    # Final score
    total_combined_weights = sum(combined_weights.values())
    if total_combined_weights > 0:
        final_score = (
            combined_weights["tests"] * tests_score
            + combined_weights["llm"] * llm_score
        ) / total_combined_weights
    else:
        final_score = 0

    pv_data = {
        k: [(float(x) if (x != "MISS" and x is not None) else 0) for x in v]
        for k, v in list(pvcheck_csv_scores.items())[2:]
    }

    return {
        "pvcheck": pv_data,
        "tests_scores": {**report_metrics, "final": tests_score},
        "llm_scores": {**llm_metrics_spec, "final": llm_score},
        "final_score": final_score,
        "weights": {
            "comments": comments_weights,
            "pvcheck_questions": quest_weights,
            "tests": report_weights,
            "llm": llm_weights,
            "final": combined_weights,
        },
    }
