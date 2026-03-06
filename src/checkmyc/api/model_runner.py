from .google_api import normalize_usage_gemini, run_gemini
from .openai_api import normalize_usage_openai, run_openai
from .openrouter_api import (
    normalize_usage_openrouter,
    run_openrouter,
    run_router_request,
)

PROVIDERS = {
    "openai": (run_openai, normalize_usage_openai),
    "google": (run_gemini, normalize_usage_gemini),
    "openrouter": (run_openrouter, normalize_usage_openrouter),
}


def run_model_dispatch(
    provider,
    model,
    system_prompt,
    user_prompt,
    schema,
    prompt_price,
    compl_price,
    temperature,
    debug,
):
    if provider:
        if provider == "google" or provider == "openai":
            func, _ = PROVIDERS[provider]
        else:
            func, _ = PROVIDERS["openrouter"]
        parsed, usage = func(
            system_prompt, user_prompt, schema, model, temperature, debug
        )
        return parsed, usage, provider
    parsed, usage, provider = run_router_request(
        system_prompt,
        user_prompt,
        schema,
        model,
        prompt_price,
        compl_price,
        temperature,
        debug,
    )
    return parsed, usage, provider


def normalize_usage_dispatch(provider, usage):
    if provider:
        if provider == "google" or provider == "openai":
            _, norm_func = PROVIDERS[provider]
        else:
            _, norm_func = PROVIDERS["openrouter"]
        return norm_func(usage)
    return normalize_usage_openrouter(usage)
