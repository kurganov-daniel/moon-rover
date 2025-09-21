from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Application configuration settings"""

    # Server settings
    app_host: str = '0.0.0.0'
    app_port: int = 8000

    # API settings
    api_title: str = 'Moon Rover API'
    api_description: str = 'API for controlling a moon rover robot'
    api_version: str = '1.0.0'

    model_config = SettingsConfigDict(
        env_file='.env', case_sensitive=False, extra='ignore'
    )


application_settings = AppSettings()
