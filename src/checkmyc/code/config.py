import json
from argparse import Namespace
from dataclasses import dataclass
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

PROJECT_ROOT = Path(__file__).resolve().parents[3]  # repo root
PKG_ROOT = Path(__file__).resolve().parents[1]  # src/checkmyc
DATA_DIR = PKG_ROOT / "data"
TEMPLATES_DIR = DATA_DIR / "templates"


def generate_schema(topics: list[str]) -> dict:
    n = len(topics)
    base_schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "evaluations": {
                "type": "array",
                "minItems": n,
                "maxItems": n,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "name": {"type": "string", "enum": topics},
                        "score": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 10,
                            "description": (
                                "Integer number between 0 and 10. "
                                "It evaluates the topic satisfaction based exclusively "
                                "on the specifications provided by the user."
                            ),
                        },
                        "evidences": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "additionalProperties": False,
                                "properties": {
                                    "comment": {"type": "string"},
                                    "lines": {
                                        "type": "array",
                                        "items": {
                                            "type": "string",
                                            "pattern": "^\\d+(-\\d+)?$",
                                        },
                                        "default": [],
                                    },
                                    "criticality": {
                                        "type": "string",
                                        "enum": ["high", "medium", "low"],
                                    },
                                    "goodness": {"type": "string", "enum": ["+", "-"]},
                                },
                                "required": [
                                    "comment",
                                    "lines",
                                    "criticality",
                                    "goodness",
                                ],
                            },
                        },
                    },
                    "required": ["name", "score", "evidences"],
                },
                "description": f"Must contain exactly {n} items, one per topic.",
            },
            "priority issues": {"type": "array", "items": {"type": "string"}},
            "practical_tips": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["evaluations", "priority issues", "practical_tips"],
    }
    return base_schema


def save_json_and_html(
    program_info, output_path, parsed, model, provider, tokens, call_cost, combined
):
    """Save JSON and HTML report from parsed evaluation data"""
    output_data = {
        "program": program_info,
        "LLM": parsed,
        "model": {"name": model, "provider": provider},
        "usage": tokens,
        "call_cost": call_cost,
        **combined,
    }

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"Output saved in {output_path}")

    env = Environment(loader=FileSystemLoader([str(TEMPLATES_DIR), str(PROJECT_ROOT)]))
    template = env.get_template("report_template.html")
    html_output = template.render(data=output_data)

    output_html = output_path.with_suffix(".html")
    with output_html.open("w", encoding="utf-8") as f:
        f.write(html_output)


def build_prompt_context(topics, analysis):
    """Combine topics and scripts markdowns into a single string"""
    parts = []
    for topic in topics:
        desc_path = _resolve_path(topic.get("description"), base=DATA_DIR / "topics")
        if desc_path and Path(desc_path).exists():
            parts.append(load_file(desc_path))
        else:
            parts.append(topic.get("description", ""))
    for a in analysis:
        parts.append(f"### {a['name']}\n{a['description']}")
    return "\n".join(parts)


def render_prompts(sys_prompt_path, usr_prompt_path, context_dict):
    """Render Jinja2 templates for system and user prompts."""
    # resolve to Path; allow passing either file or directory + filename
    sys_p = Path(sys_prompt_path)
    usr_p = Path(usr_prompt_path)

    loader_dirs = []
    if sys_p.parent.exists():
        loader_dirs.append(str(sys_p.parent))
    if usr_p.parent.exists():
        loader_dirs.append(str(usr_p.parent))

    sys_env = Environment(
        loader=FileSystemLoader(loader_dirs[0]), autoescape=select_autoescape()
    )
    usr_env = Environment(
        loader=FileSystemLoader(loader_dirs[1]), autoescape=select_autoescape()
    )

    sys_template = sys_env.get_template(sys_p.name)
    usr_template = usr_env.get_template(usr_p.name)

    system_prompt = sys_template.render(context_dict)
    user_prompt = usr_template.render(context_dict)

    return system_prompt, user_prompt


@dataclass
class ExamContext:
    context: str
    solution: str
    program_input: str
    quest_weights: dict
    pvcheck_flag: bool
    exam_path: Path | None


def load_exam_context(input_args, paths, questions) -> tuple[bool, ExamContext]:
    exam_dir = bool(input_args.exam)

    if exam_dir:
        exam_path = paths.get("exam_text")
        if not exam_path.exists() or not exam_path.is_dir():
            raise FileNotFoundError(f"Exam dir not found: {exam_path}")

        entries = {e.name for e in exam_path.iterdir() if e.is_file()}
        pvcheck_flag = "pvcheck.test" in entries
        dat_files = [f for f in entries if f.endswith(".dat")]
        md_files = [f for f in entries if f.endswith(".md")]
        solutions = [f for f in entries if f.endswith(".c")]
        if not (pvcheck_flag and dat_files and md_files and solutions):
            raise FileNotFoundError("Missing --exam required files")

        quest_weights = questions["questions_weights"]
        program_input = exam_path / dat_files[0]
        file_target = exam_path / md_files[0]
        sol_program = exam_path / solutions[0]
    else:
        pvcheck_flag = False
        quest_weights = {}
        program_input = paths.get("input")
        file_target = paths.get("context")
        sol_program = paths.get("solution")

    context = load_file(file_target) if Path(file_target).is_file() else ""
    if context:
        context = f"```markdown\n{context}\n```"

    solution = load_file(sol_program) if Path(sol_program).is_file() else ""

    return exam_dir, ExamContext(
        context,
        solution,
        program_input if Path(program_input).is_file() else "",
        quest_weights,
        pvcheck_flag,
        exam_path if exam_dir else None,
    )


def _resolve_path(p: str | None, base: Path | None = None) -> Path | None:
    """Resolve a path string to an absolute Path. If p is None or empty return None."""
    if not p:
        return None
    pth = Path(p)
    if pth.is_absolute():
        return pth
    if base:
        return (Path(base) / p).resolve()
    # relative to project root
    return (PROJECT_ROOT / p).resolve()


def get_paths(config: dict, config_flag: bool, args: Namespace) -> dict:
    """Return file paths from the TOML configuration, with optional overrides.
    Paths are resolved absolute against PROJECT_ROOT when they are relative.
    """
    base = config.get("paths", {})

    def r(p):
        return _resolve_path(p, base=PROJECT_ROOT)

    paths = {
        "llm_config": r(base.get("llm")),
        "questions_config": r(base.get("questions")),
        "output": r(Path(base.get("output_path")) / (args.output or "")),
    }
    if config_flag:
        paths.update(
            {
                "programs": r(Path(base.get("programs_path")) / args.program),
                "exam_text": r(Path(base.get("exam_text_path")) / (args.exam or "")),
                "sys_prompt": r(Path(base.get("sys_prompt_path")) / args.system_prompt),
                "usr_prompt": r(Path(base.get("usr_prompt_path")) / args.user_prompt),
                "input": r(Path(base.get("exam_text_path")) / (args.input or "")),
                "context": r(Path(base.get("exam_text_path")) / (args.context or "")),
                "solution": r(Path(base.get("exam_text_path")) / (args.solution or "")),
            }
        )
    else:
        # sensible defaults when not using config paths (all must be specified in the cli)
        paths.update(
            {
                "programs": args.program,
                "exam_text": args.exam or "",
                "sys_prompt": args.system_prompt,
                "usr_prompt": args.user_prompt,
            }
        )

    return paths


def load_file(path: str | Path, mode="r", encoding="utf-8"):
    """Load text or JSON file based on its extension. Return empty string if path is falsy."""
    if not path:
        return ""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {p}")
    with p.open(mode, encoding=encoding) as f:
        return json.load(f) if str(p).endswith(".json") else f.read()


def programs_loading(paths, extension):
    """Get programs names to be evaluated. Return empty string if path is falsy."""
    p = paths.get("programs")
    if not p.exists():
        raise FileNotFoundError(f"Program file or directory not found: {p}")
    if p.is_file() and p.suffix == extension:
        # single program case
        program_paths = [p]
    elif p.is_dir():
        # directory case
        program_paths = [
            p / prog
            for prog in p.iterdir()
            if (prog.is_file() and prog.suffix == extension)
        ]
        if not program_paths:
            raise FileNotFoundError(
                f"Program files not found in {p} with extension {extension}"
            )
    else:
        raise TypeError(f"Wrong program file extension: {p}")

    return program_paths
