"""Configuration settings for Helix ALM MCP Server."""

from pydantic_settings import BaseSettings
from pydantic import Field


# --- Pagination Defaults ---
DEFAULT_PAGE = 1
DEFAULT_REQUIREMENTS_PER_PAGE = 50
DEFAULT_DOCUMENTS_PER_PAGE = 25
MAX_PER_PAGE = 300

# --- Requirement Field IDs ---
# Used when building API payloads for create/update operations
FIELD_ID_REQ_SUMMARY = 2
FIELD_ID_REQ_DESCRIPTION = 7

# --- Document Field IDs ---
FIELD_ID_DOC_NAME = 2
FIELD_ID_DOC_DESCRIPTION = 3
FIELD_ID_DOC_TYPE = 301

# --- Requirement Type ID Mapping ---
# Maps user-friendly type names to Helix ALM internal IDs
REQUIREMENT_TYPE_MAP = {
    "User Story": 4,
    "Task": 5,
    "Overview": 6,
    "Functional Requirement": 7,
    "Business Requirement": 8,
    "Non-Functional Requirement": 9,
    "Design Note": 10,
    "Software  Requirements": 11,
    "Security Requirement": 12,
    "Technical Requirement": 13,
    "Hardware Requirements": 14,
    "Risk": 15,
    "Performance Requirement": 17,
    "Use Case": 18,
    "Compliance Requirement": 19,
    "Glossary": 20,
    "Hazards": 22,
    "Harms": 23,
}
DEFAULT_REQUIREMENT_TYPE = "Functional Requirement"
DEFAULT_REQUIREMENT_TYPE_ID = REQUIREMENT_TYPE_MAP[DEFAULT_REQUIREMENT_TYPE]

# --- Document Type ID Mapping ---
DOCUMENT_TYPE_MAP = {
    "PRD": 86,
    "MRD": 87,
    "FMEA": 98,
    "EPIC": 132,
}
DEFAULT_DOCUMENT_TYPE = "PRD"
DEFAULT_DOCUMENT_TYPE_ID = DOCUMENT_TYPE_MAP[DEFAULT_DOCUMENT_TYPE]

# --- HTTP Client Settings ---
HTTP_TIMEOUT = 30.0
BACKOFF_MULTIPLIER = 2


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
