"""Integration tests for MCP tool handlers.

These tests verify that the MCP tools correctly handle identifier resolution
and return expected data from the Helix ALM API.
"""

import pytest
import json
from helix_alm_mcp.server import call_tool
from tests.fixtures.sample_data import REQUIREMENTS, DOCUMENTS


class TestGetRequirementTool:
    """Tests for get_requirement tool handler."""

    @pytest.mark.asyncio
    async def test_get_by_tag(self):
        """Get requirement by tag returns correct data."""
        req = REQUIREMENTS["business_need"]
        result = await call_tool("get_requirement", {"tag": req["tag"]})

        response = json.loads(result[0].text)
        assert response["id"] == req["record_id"]
        assert response["tag"] == req["tag"]
        assert response["number"] == req["number"]

    @pytest.mark.asyncio
    async def test_get_by_number(self):
        """Get requirement by number returns correct data."""
        req = REQUIREMENTS["business_need"]
        result = await call_tool("get_requirement", {"number": req["number"]})

        response = json.loads(result[0].text)
        assert response["id"] == req["record_id"]
        assert response["tag"] == req["tag"]

    @pytest.mark.asyncio
    async def test_get_by_record_id(self):
        """Get requirement by record_id returns correct data."""
        req = REQUIREMENTS["business_need"]
        result = await call_tool("get_requirement", {"record_id": req["record_id"]})

        response = json.loads(result[0].text)
        assert response["tag"] == req["tag"]
        assert response["number"] == req["number"]

    @pytest.mark.asyncio
    async def test_get_nonexistent_returns_error(self):
        """Get nonexistent requirement returns error message."""
        result = await call_tool("get_requirement", {"tag": "NONEXISTENT-99999"})

        # Should contain error text, not raise exception
        assert "Error" in result[0].text or "not found" in result[0].text

    @pytest.mark.asyncio
    async def test_get_no_identifier_returns_error(self):
        """Get with no identifier returns error message."""
        result = await call_tool("get_requirement", {})

        assert "Error" in result[0].text or "exactly one" in result[0].text


class TestGetDocumentRequirementsTool:
    """Tests for get_document_requirements tool handler."""

    @pytest.mark.asyncio
    async def test_get_by_number(self):
        """Get document requirements by number returns requirements."""
        doc = DOCUMENTS["test_1"]
        result = await call_tool("get_document_requirements", {"number": doc["number"]})

        response = json.loads(result[0].text)
        # Verify we got requirements back (use >= since server state may grow)
        assert "requirements" in response
        assert len(response["requirements"]) >= doc["requirement_count"]

    @pytest.mark.asyncio
    async def test_get_by_tag(self):
        """Get document requirements by tag returns requirements."""
        doc = DOCUMENTS["test_1"]
        result = await call_tool("get_document_requirements", {"tag": doc["tag"]})

        response = json.loads(result[0].text)
        assert "requirements" in response
        assert len(response["requirements"]) >= doc["requirement_count"]

    @pytest.mark.asyncio
    async def test_get_empty_document(self):
        """Get requirements from empty document returns empty list."""
        doc = DOCUMENTS["test_2"]  # Has 0 requirements
        result = await call_tool("get_document_requirements", {"number": doc["number"]})

        response = json.loads(result[0].text)
        assert "requirements" in response
        assert len(response["requirements"]) == 0

    @pytest.mark.asyncio
    async def test_get_with_pagination(self):
        """Get document requirements with pagination parameters."""
        doc = DOCUMENTS["headphone_5"]  # Has 27 requirements
        result = await call_tool("get_document_requirements", {
            "number": doc["number"],
            "page": 1,
            "per_page": 10
        })

        response = json.loads(result[0].text)
        assert "requirements" in response
        # Should respect per_page limit
        assert len(response["requirements"]) <= 10


class TestUpdateRequirementTool:
    """Tests for update_requirement tool handler."""

    @pytest.mark.asyncio
    async def test_identifier_resolution_by_tag(self):
        """Update by tag resolves identifier correctly."""
        req = REQUIREMENTS["business_need"]
        try:
            result = await call_tool("update_requirement", {
                "tag": req["tag"],
                "summary": "Test Update - Identifier Resolution Test"
            })
            assert result is not None
            assert not result[0].text.startswith("Error")
        finally:
            await call_tool("update_requirement", {
                "record_id": req["record_id"],
                "summary": req["summary"],
            })

    @pytest.mark.asyncio
    async def test_identifier_resolution_by_number(self):
        """Update by number resolves identifier correctly."""
        req = REQUIREMENTS["business_need"]
        try:
            result = await call_tool("update_requirement", {
                "number": req["number"],
                "summary": "Test Update - Identifier Resolution Test"
            })
            assert result is not None
            assert not result[0].text.startswith("Error")
        finally:
            await call_tool("update_requirement", {
                "record_id": req["record_id"],
                "summary": req["summary"],
            })

    @pytest.mark.asyncio
    async def test_update_nonexistent_returns_error(self):
        """Update nonexistent requirement returns error."""
        result = await call_tool("update_requirement", {
            "tag": "NONEXISTENT-99999",
            "summary": "Should Fail"
        })
        assert "Error" in result[0].text or "not found" in result[0].text

    @pytest.mark.asyncio
    async def test_update_no_fields_returns_error(self):
        """Update with no fields to change returns error."""
        req = REQUIREMENTS["business_need"]
        result = await call_tool("update_requirement", {
            "record_id": req["record_id"],
        })
        assert "Error" in result[0].text

    @pytest.mark.asyncio
    async def test_update_summary_persists(self):
        """Update summary actually persists the change."""
        req = REQUIREMENTS["user_accounts"]
        new_summary = "Persistence Test - Updated Summary"
        try:
            result = await call_tool("update_requirement", {
                "record_id": req["record_id"],
                "summary": new_summary,
            })
            response = json.loads(result[0].text)

            # The returned requirement should have the updated summary
            updated_summary = None
            for field in response.get("fields", []):
                if field.get("label") == "Summary":
                    updated_summary = field.get("string")
                    break
            assert updated_summary == new_summary
        finally:
            await call_tool("update_requirement", {
                "record_id": req["record_id"],
                "summary": req["summary"],
            })

    @pytest.mark.asyncio
    async def test_update_description_persists(self):
        """Update description actually persists the change."""
        req = REQUIREMENTS["user_accounts"]
        new_description = "<p>Persistence Test - Updated Description</p>"
        try:
            result = await call_tool("update_requirement", {
                "record_id": req["record_id"],
                "description": new_description,
            })
            response = json.loads(result[0].text)

            updated_desc = None
            for field in response.get("fields", []):
                if field.get("label") == "Description":
                    updated_desc = field.get("formattedString", {}).get("text")
                    break
            assert new_description in (updated_desc or "")
        finally:
            # Restore by setting description back (use a known safe value)
            await call_tool("update_requirement", {
                "record_id": req["record_id"],
                "description": "User Accounts",
            })

    @pytest.mark.asyncio
    async def test_update_both_fields_persists(self):
        """Update both summary and description in a single call."""
        req = REQUIREMENTS["order_lookup"]
        new_summary = "Both Fields Test"
        new_description = "<p>Both fields updated</p>"
        try:
            result = await call_tool("update_requirement", {
                "record_id": req["record_id"],
                "summary": new_summary,
                "description": new_description,
            })
            response = json.loads(result[0].text)

            for field in response.get("fields", []):
                if field.get("label") == "Summary":
                    assert field.get("string") == new_summary
                elif field.get("label") == "Description":
                    assert new_description in field.get("formattedString", {}).get("text", "")
        finally:
            await call_tool("update_requirement", {
                "record_id": req["record_id"],
                "summary": req["summary"],
                "description": "Order Look-up",
            })


class TestSearchRequirementsTool:
    """Tests for search_requirements tool handler."""

    @pytest.mark.asyncio
    async def test_search_by_tag(self):
        """Search by tag query returns matching requirement."""
        req = REQUIREMENTS["business_need"]
        result = await call_tool("search_requirements", {
            "query": f"Tag = '{req['tag']}'"
        })

        response = json.loads(result[0].text)
        assert "requirements" in response
        assert len(response["requirements"]) >= 1
        # First result should match our tag
        assert response["requirements"][0]["tag"] == req["tag"]

    @pytest.mark.asyncio
    async def test_search_by_summary_contains(self):
        """Search by summary CONTAINS returns matching requirements."""
        result = await call_tool("search_requirements", {
            "query": "Summary CONTAINS 'Order'"
        })

        response = json.loads(result[0].text)
        assert "requirements" in response
        # Should find at least the "Order Look-up" requirement
        assert len(response["requirements"]) >= 1


class TestListRequirementsTool:
    """Tests for list_requirements tool handler."""

    @pytest.mark.asyncio
    async def test_list_with_pagination(self):
        """List requirements with pagination returns limited results."""
        result = await call_tool("list_requirements", {
            "page": 1,
            "per_page": 5
        })

        response = json.loads(result[0].text)
        assert "requirements" in response
        assert len(response["requirements"]) <= 5

    @pytest.mark.asyncio
    async def test_list_with_search(self):
        """List requirements with search filter."""
        result = await call_tool("list_requirements", {
            "search": "Tag = 'BR-1960'"
        })

        response = json.loads(result[0].text)
        assert "requirements" in response
        assert len(response["requirements"]) == 1


class TestListRequirementDocumentsTool:
    """Tests for list_requirement_documents tool handler."""

    @pytest.mark.asyncio
    async def test_list_documents(self):
        """List documents returns document array."""
        result = await call_tool("list_requirement_documents", {})

        response = json.loads(result[0].text)
        assert "documents" in response
        # Should have at least the documents we know about
        assert len(response["documents"]) >= len(DOCUMENTS)


class TestAddRequirementsToDocumentTool:
    """Tests for add_requirements_to_document tool handler.

    Tests that add requirements create a fresh document to avoid
    polluting existing test data. The document persists as test debris.
    """

    @pytest.mark.asyncio
    async def test_add_single_requirement(self):
        """Add a single requirement to a fresh document."""
        # Create a fresh document
        doc_result = await call_tool("create_requirement_document", {
            "name": "Add-Req Test - Single",
            "document_type": "PRD",
        })
        doc_response = json.loads(doc_result[0].text)
        doc_id = doc_response["documents"][0]["id"]

        req = REQUIREMENTS["business_need"]
        result = await call_tool("add_requirements_to_document", {
            "record_id": doc_id,
            "requirement_ids": [req["record_id"]],
        })
        assert not result[0].text.startswith("Error")

    @pytest.mark.asyncio
    async def test_add_multiple_requirements(self):
        """Add multiple requirements to a fresh document."""
        doc_result = await call_tool("create_requirement_document", {
            "name": "Add-Req Test - Multiple",
            "document_type": "PRD",
        })
        doc_response = json.loads(doc_result[0].text)
        doc_id = doc_response["documents"][0]["id"]

        req1 = REQUIREMENTS["user_accounts"]
        req2 = REQUIREMENTS["order_lookup"]
        result = await call_tool("add_requirements_to_document", {
            "record_id": doc_id,
            "requirement_ids": [req1["record_id"], req2["record_id"]],
        })
        assert not result[0].text.startswith("Error")

    @pytest.mark.asyncio
    async def test_add_with_document_tag_resolution(self):
        """Add requirements using document tag identifier."""
        # Create a fresh document, then look it up by tag
        doc_result = await call_tool("create_requirement_document", {
            "name": "Add-Req Test - Tag Resolution",
            "document_type": "PRD",
        })
        doc_response = json.loads(doc_result[0].text)
        doc_tag = doc_response["documents"][0]["tag"]

        req = REQUIREMENTS["business_need"]
        result = await call_tool("add_requirements_to_document", {
            "tag": doc_tag,
            "requirement_ids": [req["record_id"]],
        })
        assert not result[0].text.startswith("Error")

    @pytest.mark.asyncio
    async def test_add_with_document_number_resolution(self):
        """Add requirements using document number identifier."""
        # Create a fresh document, then look it up by number
        doc_result = await call_tool("create_requirement_document", {
            "name": "Add-Req Test - Number Resolution",
            "document_type": "PRD",
        })
        doc_response = json.loads(doc_result[0].text)
        doc_number = doc_response["documents"][0]["number"]

        req = REQUIREMENTS["user_accounts"]
        result = await call_tool("add_requirements_to_document", {
            "number": doc_number,
            "requirement_ids": [req["record_id"]],
        })
        assert not result[0].text.startswith("Error")

    @pytest.mark.asyncio
    async def test_empty_requirement_ids_returns_error(self):
        """Empty requirement_ids list returns error."""
        doc = DOCUMENTS["test_1"]
        result = await call_tool("add_requirements_to_document", {
            "number": doc["number"],
            "requirement_ids": [],
        })
        assert result[0].text.startswith("Error")

    @pytest.mark.asyncio
    async def test_no_document_identifier_returns_error(self):
        """No document identifier returns error."""
        result = await call_tool("add_requirements_to_document", {
            "requirement_ids": [1],
        })
        assert result[0].text.startswith("Error")
