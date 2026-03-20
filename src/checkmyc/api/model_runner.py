from .google_api import GeminiProvider
from .openai_api import OpenAIProvider
from .openrouter_api import OpenRouterProvider, OpenRouterRequestProvider


def get_provider(provider_name, key, **kwargs):
    providers = {
        "openai": OpenAIProvider,
        "google": GeminiProvider,
        "openrouter": OpenRouterProvider,
        "openrouter_request": OpenRouterRequestProvider,
    }

    if provider_name == "":
        provider_to_use = "openrouter_request"
    elif provider_name not in providers:
        provider_to_use = "openrouter"
    else:
        provider_to_use = provider_name
    provider_class = providers.get(provider_to_use)

    return provider_class(provider_to_use, key, **kwargs)
