from pydantic_settings import BaseSettings, SettingsConfigDict


class BasicAuthSettings(BaseSettings):
    """Basic auth configuration from environment"""

    USERNAME: str = 'admin'
    PASSWORD: str = 'moon-rover-secret'

    model_config = SettingsConfigDict(extra='ignore')
