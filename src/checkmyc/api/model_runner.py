from .google_api import GeminiProvider
from .openai_api import OpenAIProvider
from .openrouter_api import OpenRouterProvider


def get_provider(provider_name):
    providers = {
        "openai": OpenAIProvider,
        "google": GeminiProvider,
        "openrouter": OpenRouterProvider,
    }

    provider_class = (
        providers.get(provider_name)
        if provider_name in providers
        else providers.get("openrouter")
    )

    return provider_class()
