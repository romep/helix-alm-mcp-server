"""Pydantic models for Helix ALM data types."""

from pydantic import BaseModel, Field


class Requirement(BaseModel):
    """A requirement from Helix ALM."""

    id: int | None = Field(default=None, description="Requirement ID")
    number: int | None = Field(default=None, description="Requirement number")
    summary: str | None = Field(default=None, description="Requirement summary/title")
    description: str | None = Field(default=None, description="Detailed description")
    tag: str | None = Field(default=None, description="Requirement tag")

    # Allow extra fields since Helix ALM has many configurable fields
    model_config = {"extra": "allow"}


class RequirementList(BaseModel):
    """Response from listing requirements."""

    requirements: list[dict] = Field(default_factory=list)
    paging: dict | None = Field(default=None, description="Pagination info")


class CreateRequirementInput(BaseModel):
    """Input for creating a new requirement."""

    summary: str = Field(description="Requirement summary/title")
    description: str | None = Field(default=None, description="Detailed description")
    tag: str | None = Field(default=None, description="Requirement tag")

    model_config = {"extra": "allow"}


class UpdateRequirementInput(BaseModel):
    """Input for updating a requirement."""

    summary: str | None = Field(default=None, description="Requirement summary/title")
    description: str | None = Field(default=None, description="Detailed description")
    tag: str | None = Field(default=None, description="Requirement tag")

    model_config = {"extra": "allow"}
