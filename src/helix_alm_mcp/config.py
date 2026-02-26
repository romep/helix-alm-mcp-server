"""Configuration settings for Helix ALM MCP Server."""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Connection
    helix_alm_api_url: str = Field(
        default="https://tryhelixalm.perforce.com:8443/helix-alm/api/v0",
        description="Helix ALM REST API base URL",
    )
    helix_alm_project: str = Field(
        default="",
        description="Helix ALM project name",
    )

    # API Key Authentication (recommended)
    helix_alm_api_key: str | None = Field(
        default=None,
        description="Helix ALM API key",
    )
    helix_alm_api_secret: str | None = Field(
        default=None,
        description="Helix ALM API secret",
    )

    # Rate Limiting
    rate_limit_retry_max: int = Field(
        default=5,
        description="Maximum number of retry attempts on HTTP 429",
    )
    rate_limit_retry_delay: float = Field(
        default=1.0,
        description="Initial backoff delay in seconds for rate-limit retries",
    )
    test_inter_request_delay: float = Field(
        default=1.0,
        description="Delay in seconds between test API calls to avoid rate limiting",
    )

    # Basic Authentication (alternative)
    helix_alm_username: str | None = Field(
        default=None,
        description="Helix ALM username for basic auth",
    )
    helix_alm_password: str | None = Field(
        default=None,
        description="Helix ALM password for basic auth",
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    @property
    def has_api_key_auth(self) -> bool:
        """Check if API key authentication is configured."""
        return bool(self.helix_alm_api_key and self.helix_alm_api_secret)

    @property
    def has_basic_auth(self) -> bool:
        """Check if basic authentication is configured."""
        return bool(self.helix_alm_username and self.helix_alm_password)


settings = Settings()
