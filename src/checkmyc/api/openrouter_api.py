import json
from typing import re

import openai
import requests
from openai import OpenAI

from ..api.utils_api import (
    BaseProvider,
    FatalAPIError,
    InvalidResponseError,
    TransientAPIError,
)


def normalize_usage2(usage: dict) -> dict:
    t_input = usage.get("prompt_tokens") or 0
    output = usage.get("output_tokens") or 0
    input_details = usage.get("prompt_tokens_details") or {}
    output_details = usage.get("completion_tokens_details") or {}
    in_cached = input_details.get("cached_tokens") or 0
    out_cached = output_details.get("cached_tokens") or 0
    return {
        "prompt_tokens": t_input - in_cached,
        "completion_tokens": output - out_cached,
        "cached_tokens": in_cached + out_cached,
        "total_tokens": usage.get("total_tokens") or 0,
    }


class OpenRouterProvider(BaseProvider):
    def __init__(self):
        key = self.check_api_key("OPENROUTER_API_KEY2")
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=key,
            max_retries=0,
            timeout=120.0,
        )

    def run(self, sys_prompt, usr_prompt, schema, model, temperature):
        """Execute an API call using OpenRouter with structured JSON output"""
        try:
            response = self.client.responses.create(
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
                prompt_cache_retention="in-memory",  # "in-memory"
                prompt_cache_key="checkmyc",
            )
            return response.output[0].content[0].text, response.usage
        except (
            openai.RateLimitError,
            openai.APITimeoutError,
            openai.APIConnectionError,
            openai.InternalServerError,
        ) as e:
            raise TransientAPIError(f"API Error: {e}") from e
        except (openai.APIError, openai.AuthenticationError, InvalidResponseError) as e:
            raise FatalAPIError(f"API Error: {e}") from e

    def normalize_usage(self, usage: dict) -> dict:
        t_input = usage.get("input_tokens") or 0
        details = usage.get("input_tokens_details") or {}
        cached = details.get("cached_tokens") or 0
        return {
            "prompt_tokens": t_input - cached,
            "completion_tokens": usage.get("output_tokens") or 0,
            "cached_tokens": cached,
            "total_tokens": usage.get("total_tokens") or 0,
        }


"""
def run_openrouter(sys_prompt, usr_prompt, schema, model, temperature):
    key = "aa"
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

    # Robust aggregation
    message = getattr(response.choices[0], "message", {})
    content = getattr(message, "content", "").strip()

    ##########
    if debug:
        save_debug_pair(content, response.usage.model_dump(), "debugs")

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
        save_debug_pair(content, response.usage, "failures")
        raise InvalidResponseError(f"Invalid JSON in response: {content}") from e

    return parsed, response.usage.model_dump()
    """


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
    # key = check_api_key("OPENROUTER_API_KEY2")
    key = "aa"

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
