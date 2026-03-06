import json
import logging

import openai
from openai import OpenAI

from ..api.utils_api import (
    FatalAPIError,
    InvalidResponseError,
    TransientAPIError,
    check_api_key,
)

logger = logging.getLogger(__name__)


def normalize_usage_openai(usage: dict) -> dict:
    return {
        "prompt_tokens": usage.get("input_tokens", 0),
        "completion_tokens": usage.get("output_tokens", 0),
        "cached_tokens": usage.get("cached_tokens", 0),
        "total_tokens": usage.get("total_tokens", usage.get("total", 0)),
    }


def run_openai(sys_prompt, usr_prompt, schema, model, temperature, debug):
    key = check_api_key("OPENAI_API_KEY")
    client = OpenAI(api_key=key, max_retries=0, timeout=120.0)
    try:
        response = client.responses.create(
            model=model,
            input=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": usr_prompt},
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "response_schema",
                    "strict": True,
                    "schema": schema,
                }
            },
            temperature=temperature,
        )
    except (
        openai.RateLimitError,
        openai.APITimeoutError,
        openai.APIConnectionError,
        openai.InternalServerError,
    ) as e:
        raise TransientAPIError(f"API Error: {e}") from e
    except (openai.APIError, openai.AuthenticationError, InvalidResponseError) as e:
        raise FatalAPIError(f"API Error: {e}") from e

    if debug:
        print(response)

    try:
        text = response.output[0].content[0].text
        parsed = json.loads(text)
    except (AttributeError, IndexError, json.JSONDecodeError) as e:
        raise InvalidResponseError("[TRANSIENT] Invalid JSON in response.") from e
    return parsed, response.usage.model_dump()
