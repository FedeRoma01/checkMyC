import json
from typing import re

import openai
import requests
from openai import OpenAI

from ..api.utils_api import (
    FatalAPIError,
    InvalidResponseError,
    TransientAPIError,
    check_api_key,
)


def normalize_usage_openrouter(usage: dict) -> dict:
    return {
        "prompt_tokens": getattr(usage, "prompt_tokens", 0),
        "completion_tokens": getattr(usage, "completion_tokens", 0),
        "cached_tokens": getattr(
            getattr(usage, "prompt_tokens_details", {}), "cached_tokens", 0
        )
        + getattr(getattr(usage, "completion_tokens_details", {}), "cached_tokens", 0),
        "total_tokens": getattr(usage, "total_tokens", 0),
    }


def run_openrouter(sys_prompt, usr_prompt, schema, model, temperature, debug):
    """Execute an API call using OpenRouter with structured JSON output"""
    key = check_api_key("OPENROUTER_API_KEY2")

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=key,
        max_retries=0,
        timeout=120.0,
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": usr_prompt},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "output_schema",
                    "strict": True,
                    "schema": schema,
                },
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

    # Robust aggregation
    message = getattr(response.choices[0], "message", {})
    content = getattr(message, "content", "").strip()

    # Fallback: try reasoning field if content empty
    if not content:
        reasoning = getattr(message, "reasoning", "")
        if reasoning:
            match = re.search(r"```json\s*(\{.*\})\s*```", reasoning, re.DOTALL)
            content = match.group(1).strip() if match else reasoning.strip()

    if not content:
        raise InvalidResponseError(f"Empty or malformed response: {response}")

    try:
        parsed = json.loads(content.strip())
    except json.JSONDecodeError as e:
        raise InvalidResponseError(f"Invalid JSON in response: {content}") from e

    return parsed, response.usage.model_dump()


def run_router_request(
    sys_prompt,
    usr_prompt,
    schema,
    model,
    prompt_max_price,
    completion_max_price,
    temperature,
    debug,
):
    """Execute direct OpenRouter API call with explicit provider control and price constraints."""
    key = check_api_key("OPENROUTER_API_KEY2")

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": usr_prompt},
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {"name": "output_schema", "strict": True, "schema": schema},
        },
        "provider": {
            "sort": "price",
            "max_price": {
                "prompt": prompt_max_price,
                "completion": completion_max_price,
            },
            "allow_fallbacks": True,
        },
        "temperature": temperature,
        "structured_output": True,
        "usage": {"include": True},
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        raise TransientAPIError(f"OpenRouter HTTP error: {e}") from e
    except json.JSONDecodeError as e:
        raise InvalidResponseError(
            f"Invalid JSON from OpenRouter: {response.text}"
        ) from e

    if debug:
        print(data)

    try:
        message = data["choices"][0]["message"]
        content = message.get("content", "").strip()

        # Fallback: if content empty, try to extract from reasoning field
        if not content:
            reasoning = message.get("reasoning", "")
            if reasoning:
                match = re.search(r"```json\s*(\{.*\})\s*```", reasoning, re.DOTALL)
                content = match.group(1).strip() if match else reasoning.strip()

        parsed = json.loads(content)
    except (KeyError, json.JSONDecodeError) as e:
        raise InvalidResponseError(f"Malformed OpenRouter response: {data}") from e

    return parsed, data.get("usage", {}), data.get("provider")
