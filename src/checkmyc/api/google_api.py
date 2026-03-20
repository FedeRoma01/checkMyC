from google import genai
from google.genai import errors, types

from ..api.utils_api import (
    BaseProvider,
    CacheAPIError,
    FatalAPIError,
    TransientAPIError,
)


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


class GeminiProvider(BaseProvider):
    def __init__(self, provider, key, **kwargs):
        self.key = self.check_api_key(key)
        self.client = genai.Client(api_key=self.key, http_options={"timeout": 30000})
        self.cache = None  # lazily initialized at the first API call
        self.provider = provider
        self.cache_flag = kwargs.get("cache_flag")

    def run(self, sys_prompt, usr_prompt, schema, model, temperature):
        separator = "## Evaluated Program"

        # Create explicit cache if multiple programs to be evaluated, and it is not created yet
        if self.cache is None and self.cache_flag:
            try:
                # We split to isolate the static part (context + eval prog)
                usr_parts = usr_prompt.split(separator)
                static_context = usr_parts[0]

                # Create a cache with a 5 minute TTL (300 seconds)
                self.cache = self.client.caches.create(
                    model=model,
                    config=types.CreateCachedContentConfig(
                        display_name="checkmyc",
                        system_instruction=sys_prompt,
                        contents=[
                            types.Content(
                                role="user",
                                parts=[types.Part.from_text(text=static_context)],
                            )
                        ],
                        ttl="120s",
                    ),
                )
            except Exception as e:
                raise CacheAPIError(f"Cache creation error: {e}") from e

        gemini_schema = json_to_gemini_schema(schema)

        transient_errors = [500, 429, 503, 504]
        fatal_errors = [400, 404]

        gen_config = {
            "temperature": temperature,
            "response_mime_type": "application/json",
            "response_schema": gemini_schema,
            "candidate_count": 1,
            "automatic_function_calling": types.AutomaticFunctionCallingConfig(
                disable=True
            ),
        }

        try:
            if self.cache_flag:
                passed = usr_prompt.split(separator)[1]
                gen_config["cached_content"] = self.cache.name

            else:
                passed = usr_prompt
                gen_config["system_instruction"] = sys_prompt

            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=passed)],
                )
            ]

            response = self.client.models.generate_content(
                model=model,
                contents=contents,
                config=types.GenerateContentConfig(**gen_config),
            )

            return response.text, response.usage_metadata, self.provider

        except errors.APIError as e:
            if e.code in transient_errors:
                raise TransientAPIError(e.message) from e
            elif e.code in fatal_errors:
                raise FatalAPIError(e.message) from e
            else:
                raise FatalAPIError(
                    f"Unexpected Google API Error ({e.code}): {e.message}"
                ) from e

    def normalize_usage(self, usage: dict) -> dict:
        return {
            "prompt_tokens": usage.get("prompt_token_count") or 0,
            "completion_tokens": usage.get("candidates_token_count")
            or 0 + usage.get("thoughts_token_count")
            or 0,
            "cached_tokens": usage.get("cached_content_token_count") or 0,
            "total_tokens": usage.get("total_token_count") or 0,
        }
