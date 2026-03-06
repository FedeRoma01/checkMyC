import json

from google import genai
from google.genai import errors, types

from ..api.utils_api import (
    FatalAPIError,
    InvalidResponseError,
    TransientAPIError,
    check_api_key,
    json_to_gemini_schema,
)


def normalize_usage_gemini(usage: dict) -> dict:
    return {
        "prompt_tokens": usage.get("prompt_token_count", 0),
        "completion_tokens": usage.get("candidates_token_count", 0),
        "cached_tokens": usage.get("cached_content_token_count", 0),
        "total_tokens": usage.get("total_token_count", 0),
    }


def run_gemini(sys_prompt, usr_prompt, schema, model, temperature, debug):
    # Execute a Gemini API call with structured JSON output

    key = check_api_key("GOOGLE_API_KEY2")
    gemini_schema = json_to_gemini_schema(schema)
    client = genai.Client(api_key=key)

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text=f"[SYSTEM]\n{sys_prompt}\n\n[USER]\n{usr_prompt}"
                )
            ],
        )
    ]

    transient_errors = [500, 429, 503, 504]
    fatal_errors = [400, 404]

    try:
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=types.GenerateContentConfig(
                temperature=temperature,
                response_mime_type="application/json",
                response_schema=gemini_schema,
                candidate_count=1,
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                    disable=True
                ),
            ),
        )

    except errors.APIError as e:
        if e.code in transient_errors:
            raise TransientAPIError(e.message) from e
        elif e.code in fatal_errors:
            raise FatalAPIError(e.message) from e

    if debug:
        print(response)

    try:
        parsed = json.loads(response.text)
    except json.JSONDecodeError as e:
        raise InvalidResponseError("[TRANSIENT] Invalid JSON in response.") from e

    usage_info = response.usage_metadata.model_dump() if response.usage_metadata else {}

    return parsed, usage_info
