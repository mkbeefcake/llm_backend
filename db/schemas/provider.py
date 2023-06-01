class ProviderSchema:
    def __init__(
        self, provider_name: str, provider_description: str, provider_icon_url: str
    ):
        self.provider_name = provider_name
        self.provider_description = provider_description
        self.provider_icon_url = provider_icon_url
