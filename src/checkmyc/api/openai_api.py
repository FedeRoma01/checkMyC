import openai
from openai import OpenAI

from ..api.utils_api import (
    BaseProvider,
    FatalAPIError,
    InvalidResponseError,
    TransientAPIError,
)


class OpenAIProvider(BaseProvider):
    def __init__(self):
        key = self.check_api_key("OPENAI_API_KEY")
        self.client = OpenAI(api_key=key, max_retries=0, timeout=120.0)

    def run(self, sys_prompt, usr_prompt, schema, model, temperature):
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
