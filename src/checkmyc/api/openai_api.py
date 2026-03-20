import openai
from openai import OpenAI

from ..api.utils_api import (
    BaseProvider,
    FatalAPIError,
    InvalidResponseError,
    TransientAPIError,
)


class OpenAIProvider(BaseProvider):
    def __init__(self, provider, key, **kwargs):
        self.key = self.check_api_key(key)
        self.client = OpenAI(api_key=self.key, max_retries=0, timeout=30.0)
        self.provider = provider

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
                prompt_cache_retention="in_memory",
                prompt_cache_key="checkmyc",
            )
            return response.output[0].content[0].text, response.usage, self.provider
        except (
            openai.RateLimitError,
            openai.APITimeoutError,
            openai.APIConnectionError,
            openai.InternalServerError,
        ) as e:
            raise TransientAPIError(e) from e
        except (openai.APIError, openai.AuthenticationError, InvalidResponseError) as e:
            raise FatalAPIError(e) from e
        except Exception as e:
            raise Exception(e) from e

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
