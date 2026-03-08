import json
import logging
import os
import sys
from abc import ABC, abstractmethod
from datetime import datetime


class TransientAPIError(Exception):
    pass


class FatalAPIError(Exception):
    pass


class CacheAPIError(Exception):
    pass


class InvalidResponseError(TransientAPIError):
    pass


logger = logging.getLogger(__name__)


class BaseProvider(ABC):
    def check_api_key(self, env_var) -> str:
        """Check the presence of the API key used"""
        key = os.getenv(env_var)
        if not key:
            logger.error(f"Missing key {env_var}")
            sys.exit(1)
        return key

    @abstractmethod
    def run(self, sys_prompt, usr_prompt, schema, model, temperature):
        """Execute specific API call"""
        pass

    @abstractmethod
    def normalize_usage(self, usage: dict) -> dict:
        """Normalize tokens count into a standard format (used in llm.toml)"""
        pass


def save_debug_pair(raw_text, context_data, case_folder):
    """
    Save the malformed text and a JSON context in a dedicated folder.
    """

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_folder = os.path.join("logs", case_folder, f"debug_{timestamp}")

    if not os.path.exists(session_folder):
        os.makedirs(session_folder)

    raw_path = os.path.join(session_folder, "llm_output.txt")
    with open(raw_path, "w", encoding="utf-8") as f:
        f.write(raw_text)

    context_path = os.path.join(session_folder, "context_metadata.json")
    with open(context_path, "w", encoding="utf-8") as f:
        json.dump(context_data, f, indent=4, ensure_ascii=False, default=str)

    print(f"LLM output and metadata saved for debug in: {session_folder}")


def compute_cost(model_name, tokens_count, pricing_data):
    if model_name not in pricing_data:
        return " Not specified in llm.toml"

    model_prices = pricing_data[model_name]
    tot_cost = 0
    for token_type, count in tokens_count.items():
        if token_type not in model_prices:
            continue
        rate = model_prices[token_type]  # USD per 1M tokens
        tot_cost += (count / 1000000) * rate
    return tot_cost
