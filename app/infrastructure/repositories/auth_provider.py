from pydantic_settings import BaseSettings, SettingsConfigDict


class BasicAuthSettings(BaseSettings):
    """Basic auth configuration from environment"""

    USERNAME: str
    PASSWORD: str 

    model_config = SettingsConfigDict(extra='ignore')
