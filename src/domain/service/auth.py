from src.domain.models.response import ProvidersResponse
from src.providers_config import PROVIDERS
from urllib.parse import urlencode


class AuthService:
    def __init__(self) -> None:
        pass

    @staticmethod
    def build_auth_redirect(auth_url: str, client_id: str, scopes: list, redirect_uri: str):
        params = {
            "client_id": client_id,
            "response_type": "code",  # стандартный response_type для Authorization Code Flow
            "scope": " ".join(scopes)
        }
        if redirect_uri:
            params["redirect_uri"] = redirect_uri

        query = urlencode(params)
        return f"{auth_url}?{query}"

    def get_providers(self) -> ProvidersResponse:

        return ProvidersResponse(**{
            "email_enabled": PROVIDERS.email_enabled,
            "oauth_providers": [
                {
                    "id": k,
                    "icon_url": provider.icon_url,
                    "display_name": provider.display_name,
                    "redirect_uri": self.build_auth_redirect(provider.auth_url, provider.client_id, provider.scopes, provider.redirect_uri),
                    "use_in_auth": provider.use_in_auth,
                    "limit": provider.count_limit
                } for k, provider in filter(lambda x: x[1].enabled, PROVIDERS.oauth_providers.items())
            ]
        })
