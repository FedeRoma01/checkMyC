import logging
import os
import sys

from google.genai import types


class TransientAPIError(Exception):
    pass


class FatalAPIError(Exception):
    pass


class InvalidResponseError(TransientAPIError):
    pass


logger = logging.getLogger(__name__)


def check_api_key(env_var) -> str:
    key = os.getenv(env_var)
    if not key:
        logger.error(f"Missing key {env_var}")
        sys.exit(1)
    return key


def json_to_gemini_schema(node: dict) -> types.Schema:
    """Convert a JSON Schema Draft7-like dict to google.genai.types.Schema."""
    type_map = {
        "string": types.Type.STRING,
        "number": types.Type.NUMBER,
        "integer": types.Type.INTEGER,
        "boolean": types.Type.BOOLEAN,
        "array": types.Type.ARRAY,
        "object": types.Type.OBJECT,
    }

    json_type = node.get("type")
    gem_type = type_map.get(json_type, types.Type.STRING)

    schema_kwargs = {
        "type": gem_type,
        "description": node.get("description"),
        "nullable": node.get("nullable"),
        "enum": node.get("enum"),
        "format": node.get("format"),
    }

    if "pattern" in node:
        schema_kwargs["pattern"] = node.get("pattern")
    if "minimum" in node:
        schema_kwargs["minimum"] = float(node.get("minimum"))
    if "maximum" in node:
        schema_kwargs["maximum"] = float(node.get("maximum"))

    if json_type == "array" and "items" in node:
        schema_kwargs["items"] = json_to_gemini_schema(node["items"])
        schema_kwargs["min_items"] = node.get("minItems")
        schema_kwargs["max_items"] = node.get("maxItems")

    if json_type == "object":
        properties = node.get("properties", {})
        schema_kwargs["properties"] = {
            k: json_to_gemini_schema(v) for k, v in properties.items()
        }
        schema_kwargs["required"] = node.get("required", [])

    return types.Schema(**schema_kwargs)
