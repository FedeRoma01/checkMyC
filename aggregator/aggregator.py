import argparse
import json
import os
import tomllib
from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.checkmyc.__main__ import compute_cost
from src.checkmyc.api.model_runner import normalize_usage_dispatch
from src.checkmyc.api.openai_api import run_openai
from src.checkmyc.code.config import render_prompts

# === Basic paths consistent with the repo ===
timestamp = datetime.now().strftime("%H-%M-%S")
PROJECT_ROOT = Path(__file__).resolve().parents[1]  # repo root
CMC_ROOT = PROJECT_ROOT / "src" / "checkmyc"  # src/checkmyc
CURR_DIR = Path(__file__).resolve().parents[0]  # src/checkmyc / "data"
OUTPUT_DIR = PROJECT_ROOT / "output" / "aggregation"
INPUT_DIR = PROJECT_ROOT / "output" / "comments_extraction" / "gpt-4_1-mini"


def process_json_files_single_output(
    file_paths: list[Path], output_path: str
) -> dict[str, list[dict[str, str]]]:
    """
    Process a list of JSON files to extract comments with 'goodness' == '-'.
    Group all comments by evaluation name and save the result in a single JSON file.
    Each comment is a dict with 'id' and 'text'.
    """
    grouped_comments: dict[str, list[dict[str, str]]] = {}
    comment_idx = 1  # ID counter

    for file_path in file_paths:
        try:
            with open(file_path, encoding="utf-8") as f:
                data: dict[str, Any] = json.load(f)
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            continue
        except json.JSONDecodeError:
            print(f"JSON error in: {file_path}")
            continue

        evaluations: list[dict[str, Any]] = data.get("LLM", {}).get("evaluations", [])
        for evaluation in evaluations:
            name = evaluation.get("name")
            evidences = evaluation.get("evidences", [])

            if not name:
                continue
            grouped_comments.setdefault(name, [])

            for ev in evidences:
                comment = ev.get("comment")
                goodness = ev.get("goodness")
                if (
                    goodness == "-"
                    and comment
                    and not any(c["text"] == comment for c in grouped_comments[name])
                ):
                    grouped_comments[name].append(
                        {"id": f"ID{comment_idx:03}", "text": comment}
                    )
                    comment_idx += 1

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        try:
            path = PROJECT_ROOT / output_path
            with path.open("w", encoding="utf-8") as f:
                json.dump(grouped_comments, f, indent=4, ensure_ascii=False)
            print(f"All comments extracted in: {output_path}")
        except OSError:
            print(f"Error writing output file: {output_path}")

    return grouped_comments


def get_input_files_from(files_dir: Path) -> list[Path]:
    """Returns a list of JSON file paths in a directory."""
    return [files_dir / f for f in os.listdir(files_dir) if f.endswith(".json")]


def init_argparser():
    parser = argparse.ArgumentParser(
        description="Extract different negative meaning comments per topic from "
        "different analysis"
    )
    parser.add_argument(
        "--input",
        "-i",
        type=str,
        default=INPUT_DIR,
        help="Directory containing the evaluations from "
        "which extract negative comments",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=f"{timestamp}_comments.json",
        help="Output name",
    )
    parser.add_argument(
        "--system_prompt",
        "-sp",
        type=str,
        default="sys_aggregator.md",
        help="System prompt to be used",
    )
    parser.add_argument(
        "--user_prompt",
        "-up",
        type=str,
        default="usr_aggregator.md",
        help="User prompt to be used",
    )
    parser.add_argument(
        "--schema",
        "-s",
        type=str,
        default="schema_extractor.json",
        help="Output schema to be used",
    )
    parser.add_argument(
        "--model", "-m", type=str, default="gpt-4.1-mini", help="Model to be used"
    )
    parser.add_argument(
        "--intermediate", "-int", type=str, help="Intermediate result saving path"
    )
    parser.add_argument(
        "--html_template",
        "-html",
        type=str,
        default="templ_aggregator.html",
        help="Intermediate result saving path",
    )

    return parser


def generate_schema(topics: list[str]) -> dict:
    n = len(topics)
    base_schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "topics": {
                "type": "array",
                "minItems": n,
                "maxItems": n,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "name": {"type": "string", "enum": topics},
                        "comments": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "additionalProperties": False,
                                "properties": {
                                    "comment": {"type": "string"},
                                    "list": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                    },
                                },
                                "required": ["comment", "list"],
                            },
                        },
                    },
                    "required": ["name", "comments"],
                },
            }
        },
        "required": ["topics"],
    }

    return base_schema


def reconstruct_json(parsed, preprocessed):
    """
    Rebuild final JSON substituting IDs with original comments
    """

    final_json = {"topics": []}

    for topic in parsed.get("topics", []):
        topic_name = topic.get("name", "")
        comments_list = topic.get("comments", [])

        # ID map -> comment only of the current topic
        topic_comments = preprocessed.get(topic_name, [])
        id_to_text = {c["id"]: c["text"] for c in topic_comments}

        topic_entry = {"name": topic_name, "comments": []}
        for comment_entry in comments_list:
            representative_comm = comment_entry.get("comment", "")
            cluster_ids = comment_entry.get("list", [])
            cluster_texts = [
                {"id": cid, "text": id_to_text[cid]}
                for cid in cluster_ids
                if cid in id_to_text
            ]
            topic_entry["comments"].append(
                {"comment": representative_comm, "list": cluster_texts}
            )

        final_json["topics"].append(topic_entry)

    return final_json


def main():
    # Input directory with previous results
    parser = init_argparser()
    input_args = parser.parse_args()
    input_files = get_input_files_from(input_args.input)

    # PRE-PROCESSING (Extracting and saving comments with unique ID)
    comments = process_json_files_single_output(input_files, input_args.intermediate)
    print("\nProcessing complete.")

    # LLM configuration info
    with open(CMC_ROOT / "config" / "llm.toml", "rb") as f:
        llm_config = tomllib.load(f)
    pricing = llm_config.get("models", {})

    topic_list = [t["name"] for t in llm_config.get("topics", {})]
    tot_cost = 0
    tot_json = {"topics": []}

    # BATCHING AGGREGATION (to avoid API call failure)
    for topic in topic_list:
        # PROMPT CONSTRUCTION
        templ_context = {"comments": {f"{topic}": comments[topic]}}
        system_prompt, user_prompt = render_prompts(
            CURR_DIR / input_args.system_prompt,
            CURR_DIR / input_args.user_prompt,
            templ_context,
        )

        # OUTPUT JSON SCHEMA
        schema = generate_schema([topic])

        # API CALL
        parsed, usage = run_openai(
            system_prompt, user_prompt, schema, input_args.model, 0.3, False
        )

        tokens = normalize_usage_dispatch("openai", usage)
        call_cost = compute_cost(input_args.model, tokens, pricing)

        # TOPIC AGGREGATION (each topic, once used, is added in the final aggregation)
        tot_cost += call_cost
        tot_json["topics"].append(parsed["topics"][0])

    # POST-PROCESSING
    final_json = reconstruct_json(tot_json, comments)

    # OUTPUT
    final_json["cost"] = tot_cost

    # JSON SAVING
    output_json = OUTPUT_DIR / input_args.model / input_args.output
    output_json.parent.mkdir(parents=True, exist_ok=True)
    with output_json.open("w", encoding="utf-8") as f:
        json.dump(final_json, f, indent=2, ensure_ascii=False)

    # HTML
    output_html = output_json.with_suffix(".html")
    env = Environment(
        loader=FileSystemLoader(CURR_DIR / "templates"),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template(input_args.html_template)
    html = template.render(data=final_json)

    # SAVING
    output_html.write_text(html, encoding="utf-8")

    print(f"Output saved to {input_args.output}")


if __name__ == "__main__":
    main()
