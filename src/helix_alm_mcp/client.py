"""Helix ALM REST API client."""

import asyncio
import base64
import logging
from urllib.parse import quote

import httpx

logger = logging.getLogger(__name__)

from .config import settings


class HelixALMClient:
    """Client for interacting with Helix ALM REST API."""

    def __init__(self):
        self.base_url = settings.helix_alm_api_url.rstrip("/")
        self.project = settings.helix_alm_project
        self._access_token: str | None = None
        self._http_client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                verify=False,  # Helix ALM often uses self-signed certs
                timeout=30.0,
            )
        return self._http_client

    async def close(self):
        """Close the HTTP client."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    def _get_initial_auth_header(self) -> dict[str, str]:
        """Get authentication header for initial auth (to get token)."""
        if settings.has_api_key_auth:
            return {
                "Authorization": f"ApiKey {settings.helix_alm_api_key}:{settings.helix_alm_api_secret}"
            }
        elif settings.has_basic_auth:
            credentials = f"{settings.helix_alm_username}:{settings.helix_alm_password}"
            encoded = base64.b64encode(credentials.encode()).decode()
            return {"Authorization": f"Basic {encoded}"}
        else:
            raise ValueError(
                "No authentication configured. Set HELIX_ALM_API_KEY/SECRET or USERNAME/PASSWORD."
            )

    def _get_bearer_auth_header(self) -> dict[str, str]:
        """Get bearer token authentication header."""
        if not self._access_token:
            raise ValueError("No access token. Call authenticate() first.")
        return {"Authorization": f"Bearer {self._access_token}"}

    @property
    def _project_url(self) -> str:
        """Get the project-specific base URL."""
        # URL-encode the project name to handle spaces
        encoded_project = quote(self.project, safe="")
        return f"{self.base_url}/{encoded_project}"

    async def authenticate(self) -> str:
        """Authenticate and get an access token."""
        client = await self._get_client()
        url = f"{self._project_url}/token"
        headers = self._get_initial_auth_header()

        for attempt in range(settings.rate_limit_retry_max + 1):
            response = await client.get(url, headers=headers)

            if response.status_code == 429 and attempt < settings.rate_limit_retry_max:
                await self._handle_rate_limit(response, attempt)
                continue

            response.raise_for_status()

            data = response.json()
            self._access_token = data["accessToken"]
            return self._access_token

        raise Exception(
            f"HTTP 429: Rate limited during authentication after "
            f"{settings.rate_limit_retry_max} retries"
        )

    async def _handle_rate_limit(self, response: httpx.Response, attempt: int) -> None:
        """Handle HTTP 429 rate limiting with exponential backoff.

        Uses the Retry-After header if present, otherwise falls back
        to exponential backoff based on settings.rate_limit_retry_delay.
        """
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            delay = float(retry_after)
        else:
            delay = settings.rate_limit_retry_delay * (2 ** attempt)
        logger.warning(
            "Rate limited (429). Retry %d/%d in %.1fs",
            attempt + 1, settings.rate_limit_retry_max, delay,
        )
        await asyncio.sleep(delay)

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: dict | None = None,
        json_data: dict | None = None,
    ) -> dict:
        """Make an authenticated request to the API with rate-limit retry."""
        if not self._access_token:
            await self.authenticate()

        client = await self._get_client()
        url = f"{self._project_url}/{endpoint.lstrip('/')}"

        for attempt in range(settings.rate_limit_retry_max + 1):
            headers = self._get_bearer_auth_header()
            headers["Accept"] = "application/json"

            if json_data:
                headers["Content-Type"] = "application/json"

            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_data,
            )

            if response.status_code == 429 and attempt < settings.rate_limit_retry_max:
                await self._handle_rate_limit(response, attempt)
                continue

            # Include response body in error for debugging
            if response.status_code >= 400:
                try:
                    error_body = response.json()
                except Exception:
                    error_body = response.text
                raise Exception(f"HTTP {response.status_code}: {error_body}")

            if response.status_code == 204:
                return {}
            return response.json()

        # Exhausted all retries on 429
        raise Exception(
            f"HTTP 429: Rate limited after {settings.rate_limit_retry_max} retries"
        )

    async def get(self, endpoint: str, params: dict | None = None) -> dict:
        """Make a GET request."""
        return await self._request("GET", endpoint, params=params)

    async def post(self, endpoint: str, data: dict) -> dict:
        """Make a POST request."""
        return await self._request("POST", endpoint, json_data=data)

    async def put(self, endpoint: str, data: dict) -> dict:
        """Make a PUT request."""
        return await self._request("PUT", endpoint, json_data=data)

    async def delete(self, endpoint: str) -> dict:
        """Make a DELETE request."""
        return await self._request("DELETE", endpoint)

    # === Requirements API ===

    async def list_requirements(
        self,
        fields: list[str] | None = None,
        search: str | None = None,
        page: int = 1,
        per_page: int = 50,
    ) -> dict:
        """List requirements with optional filtering."""
        params = {"page": page, "per_page": per_page}

        if fields:
            params["fields"] = ",".join(fields)
        if search:
            params["search"] = search

        return await self.get("requirements", params=params)

    async def get_requirement(self, requirement_id: int) -> dict:
        """Get a single requirement by ID."""
        return await self.get(f"requirements/{requirement_id}")

    async def create_requirement(
        self,
        summary: str,
        description: str | None = None,
        requirement_type_id: int = 7,  # Default to Functional Requirement
    ) -> dict:
        """Create a new requirement.

        Args:
            summary: The summary/title of the requirement
            description: Optional description (supports HTML formatting)
            requirement_type_id: Requirement type ID (default 7 = Functional Requirement)
                Known types: 4=User Story, 5=Task, 6=Overview, 7=Functional Requirement,
                8=Business Requirement, 9=Non-Functional Requirement, 10=Design Note,
                11=Software Requirements, 12=Security Requirement, 13=Technical Requirement,
                14=Hardware Requirements, 15=Risk, 17=Performance Requirement, 18=Use Case,
                19=Compliance Requirement, 20=Glossary, 22=Hazards, 23=Harms
        """
        # Build the fields array
        fields = [
            {"id": 2, "label": "Summary", "type": "string", "string": summary},
        ]

        if description:
            fields.append({
                "id": 7,
                "label": "Description",
                "type": "formattedString",
                "formattedString": {"isFormatted": True, "text": description, "inlineImages": []},
            })

        # API expects a requirements array wrapper
        data = {
            "requirements": [
                {
                    "requirementType": {"id": requirement_type_id},
                    "fields": fields,
                }
            ]
        }
        return await self.post("requirements", data)

    async def update_requirement(
        self,
        requirement_id: int,
        summary: str | None = None,
        description: str | None = None,
    ) -> dict:
        """Update an existing requirement.

        Args:
            requirement_id: Internal record ID of the requirement
            summary: New summary/title (optional)
            description: New description text, supports HTML (optional)

        Returns:
            The updated requirement (fetched after update for confirmation).
        """
        if not summary and not description:
            raise ValueError("At least one of 'summary' or 'description' must be provided")

        fields = []
        if summary is not None:
            fields.append(
                {"id": 2, "label": "Summary", "type": "string", "string": summary}
            )
        if description is not None:
            fields.append({
                "id": 7,
                "label": "Description",
                "type": "formattedString",
                "formattedString": {"isFormatted": True, "text": description, "inlineImages": []},
            })

        data = {"fields": fields}
        await self.put(f"requirements/{requirement_id}", data)

        # Fetch and return the updated requirement for confirmation
        return await self.get_requirement(requirement_id)

    async def resolve_requirement_id(
        self,
        record_id: int | None = None,
        tag: str | None = None,
        number: int | None = None,
    ) -> int:
        """Resolve a requirement identifier to internal record ID.

        Accepts one of:
        - record_id: Internal ID from API responses (pass-through)
        - tag: User-visible tag like "US-2195"
        - number: User-visible number like 2195

        Returns the internal record ID for use with API endpoints.
        Raises ValueError if not found or wrong number of identifiers provided.
        """
        provided = len([x for x in [record_id, tag, number] if x is not None])
        if provided != 1:
            raise ValueError("Provide exactly one of: record_id, tag, or number")

        if record_id is not None:
            return record_id

        if tag is not None:
            search_query = f"Tag = '{tag}'"
        else:
            search_query = f"Number = {number}"

        result = await self.list_requirements(search=search_query, per_page=1)
        requirements = result.get("requirements", [])

        if not requirements:
            identifier = tag if tag is not None else number
            raise ValueError(f"Requirement not found: {identifier}")

        return requirements[0]["id"]

    async def get_requirement_types(self) -> dict:
        """Get available requirement types."""
        return await self.get("configs/requirementTypes")

    # === Requirement Documents API ===

    async def list_requirement_documents(self) -> dict:
        """List all requirement documents."""
        return await self.get("documents")

    async def search_documents(
        self,
        search: str | None = None,
        fields: list[str] | None = None,
        page: int = 1,
        per_page: int = 50,
    ) -> dict:
        """Search documents using POST endpoint with body parameters."""
        data: dict = {"page": page, "per_page": per_page}
        if search:
            data["search"] = search
        if fields:
            data["fields"] = fields
        return await self.post("documents/search", data)

    async def resolve_document_id(
        self,
        record_id: int | None = None,
        tag: str | None = None,
        number: int | None = None,
    ) -> int:
        """Resolve a document identifier to internal record ID.

        Accepts one of:
        - record_id: Internal ID from API responses (pass-through)
        - tag: User-visible tag like "RD-108"
        - number: User-visible number like 108

        Returns the internal record ID for use with API endpoints.
        Raises ValueError if not found or wrong number of identifiers provided.

        Note: The documents API doesn't support Tag field in search queries,
        so we extract the number from the tag and search by Number instead.
        """
        provided = len([x for x in [record_id, tag, number] if x is not None])
        if provided != 1:
            raise ValueError("Provide exactly one of: record_id, tag, or number")

        if record_id is not None:
            return record_id

        # If tag provided, extract the number from it (e.g., "RD-108" → 108)
        search_number = number
        if tag is not None:
            # Tags are formatted as "RD-{number}" - extract the number portion
            try:
                search_number = int(tag.split("-")[-1])
            except (ValueError, IndexError):
                raise ValueError(f"Invalid document tag format: {tag}")

        search_query = f"Number = {search_number}"
        result = await self.search_documents(search=search_query, per_page=1)
        documents = result.get("documents", [])

        if not documents:
            identifier = tag if tag is not None else number
            raise ValueError(f"Document not found: {identifier}")

        # If we searched by tag, verify the returned document matches
        if tag is not None and documents[0].get("tag") != tag:
            raise ValueError(f"Document not found: {tag}")

        return documents[0]["id"]

    async def get_requirement_document(self, document_id: int) -> dict:
        """Get a requirement document by ID."""
        return await self.get(f"documents/{document_id}")

    async def create_requirement_document(
        self,
        name: str,
        description: str | None = None,
        document_type_id: int = 86,  # Default to PRD
    ) -> dict:
        """Create a new requirement document.

        Args:
            name: The name of the document
            description: Optional description
            document_type_id: Document type ID (default 86 = PRD)
                Known types: 86=PRD, 87=MRD, 98=FMEA, 132=EPIC
        """
        # Build the fields array
        fields = [
            {"id": 2, "label": "Name", "type": "string", "string": name},
            {"id": 301, "label": "Document Type", "type": "menuItem", "menuItem": {"id": document_type_id}},
        ]
        if description:
            fields.append({
                "id": 3,
                "label": "Description",
                "type": "formattedString",
                "formattedString": {"isFormatted": True, "text": description, "inlineImages": []},
            })

        # API expects a documents array wrapper
        data = {
            "documents": [
                {"fields": fields}
            ]
        }
        return await self.post("documents", data)

    async def get_document_requirements(
        self,
        document_id: int,
        page: int = 1,
        per_page: int = 50,
    ) -> dict:
        """Get requirements in a document.

        The Helix ALM API doesn't have a direct endpoint for document requirements.
        Instead, we get the document name and search for requirements where
        'Document List' contains that name.
        """
        # First, get the document to find its name
        document = await self.get_requirement_document(document_id)

        # Extract the document name from the fields
        document_name = None
        for field in document.get("fields", []):
            if field.get("label") == "Name":
                document_name = field.get("string")
                break

        if not document_name:
            raise ValueError(f"Could not find name for document {document_id}")

        # Search for requirements in this document
        search_query = f"'Document List' CONTAINS '{document_name}'"
        return await self.list_requirements(
            search=search_query,
            page=page,
            per_page=per_page,
        )

    async def add_requirements_to_document(
        self,
        document_id: int,
        requirement_ids: list[int],
    ) -> dict:
        """Add existing requirements to a requirement document tree (top level).

        Args:
            document_id: Internal record ID of the document
            requirement_ids: List of internal record IDs of requirements to add

        Returns:
            API response containing the created nodes.
        """
        if not requirement_ids:
            raise ValueError("requirement_ids must not be empty")

        nodes = [{"requirementID": req_id} for req_id in requirement_ids]
        return await self.post(f"documentTrees/{document_id}/nodes", {"nodesData": nodes})


def extract_field_value(requirement: dict, field_name: str) -> str | None:
    """Extract a field value from a requirement's fields array.

    Helix ALM returns fields as an array of objects with different value keys
    depending on the field type (string, integer, formattedString, etc.)
    """
    fields = requirement.get("fields", [])
    for field in fields:
        if field.get("label", "").lower() == field_name.lower():
            # Return the appropriate value based on field type
            if "string" in field:
                return field["string"]
            elif "integer" in field:
                return str(field["integer"])
            elif "formattedString" in field:
                return field["formattedString"].get("text", "")
            elif "boolean" in field:
                return str(field["boolean"])
            elif "menuItem" in field:
                return field["menuItem"].get("label", "")
            elif "user" in field:
                user = field["user"]
                return f"{user.get('firstName', '')} {user.get('lastName', '')}".strip()
            elif "date" in field:
                return field["date"]
            elif "dateTime" in field:
                return field["dateTime"]
    return None


def format_requirement_summary(requirement: dict) -> dict:
    """Format a requirement into a simplified summary."""
    return {
        "id": requirement.get("id"),
        "number": requirement.get("number"),
        "tag": requirement.get("tag"),
        "summary": extract_field_value(requirement, "Summary"),
        "status": extract_field_value(requirement, "Status"),
        "priority": extract_field_value(requirement, "Priority"),
        "requirementType": requirement.get("requirementType", {}).get("label"),
    }


# Global client instance
helix_client = HelixALMClient()
