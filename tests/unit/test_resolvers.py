"""Unit tests for identifier resolution methods.

These tests verify that the resolve_requirement_id() and resolve_document_id()
methods correctly resolve tags and numbers to internal record IDs.
"""

import pytest
from tests.fixtures.sample_data import REQUIREMENTS, DOCUMENTS


class TestResolveRequirementId:
    """Tests for resolve_requirement_id() method."""

    @pytest.mark.asyncio
    async def test_resolve_by_tag(self, client):
        """Resolve requirement by tag returns correct record_id."""
        req = REQUIREMENTS["business_need"]
        result = await client.resolve_requirement_id(tag=req["tag"])
        assert result == req["record_id"]

    @pytest.mark.asyncio
    async def test_resolve_by_number(self, client):
        """Resolve requirement by number returns correct record_id."""
        req = REQUIREMENTS["business_need"]
        result = await client.resolve_requirement_id(number=req["number"])
        assert result == req["record_id"]

    @pytest.mark.asyncio
    async def test_resolve_by_record_id_passthrough(self, client):
        """Resolve by record_id returns same value (pass-through)."""
        result = await client.resolve_requirement_id(record_id=1969)
        assert result == 1969

    @pytest.mark.asyncio
    async def test_resolve_multiple_identifiers_raises(self, client):
        """Providing multiple identifiers raises ValueError."""
        with pytest.raises(ValueError, match="exactly one"):
            await client.resolve_requirement_id(record_id=1, tag="BR-1")

    @pytest.mark.asyncio
    async def test_resolve_tag_and_number_raises(self, client):
        """Providing both tag and number raises ValueError."""
        with pytest.raises(ValueError, match="exactly one"):
            await client.resolve_requirement_id(tag="BR-1960", number=1960)

    @pytest.mark.asyncio
    async def test_resolve_all_three_raises(self, client):
        """Providing all three identifiers raises ValueError."""
        with pytest.raises(ValueError, match="exactly one"):
            await client.resolve_requirement_id(record_id=1969, tag="BR-1960", number=1960)

    @pytest.mark.asyncio
    async def test_resolve_no_identifiers_raises(self, client):
        """Providing no identifiers raises ValueError."""
        with pytest.raises(ValueError, match="exactly one"):
            await client.resolve_requirement_id()

    @pytest.mark.asyncio
    async def test_resolve_nonexistent_tag_raises(self, client):
        """Resolving nonexistent tag raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            await client.resolve_requirement_id(tag="NONEXISTENT-99999")

    @pytest.mark.asyncio
    async def test_resolve_nonexistent_number_raises(self, client):
        """Resolving nonexistent number raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            await client.resolve_requirement_id(number=99999999)

    @pytest.mark.asyncio
    async def test_resolve_different_requirement_types(self, client):
        """Resolve works for different requirement types (BR, FR, etc.)."""
        # Test Business Requirement
        br = REQUIREMENTS["business_need"]
        result_br = await client.resolve_requirement_id(tag=br["tag"])
        assert result_br == br["record_id"]

        # Test Functional Requirement
        fr = REQUIREMENTS["user_accounts"]
        result_fr = await client.resolve_requirement_id(tag=fr["tag"])
        assert result_fr == fr["record_id"]


class TestResolveDocumentId:
    """Tests for resolve_document_id() method."""

    @pytest.mark.asyncio
    async def test_resolve_by_number(self, client):
        """Resolve document by number returns an integer record_id."""
        doc = DOCUMENTS["test_1"]
        result = await client.resolve_document_id(number=doc["number"])
        assert isinstance(result, int)

    @pytest.mark.asyncio
    async def test_resolve_by_tag(self, client):
        """Resolve document by tag returns an integer record_id."""
        doc = DOCUMENTS["test_1"]
        result = await client.resolve_document_id(tag=doc["tag"])
        assert isinstance(result, int)

    @pytest.mark.asyncio
    async def test_resolve_by_record_id_passthrough(self, client):
        """Resolve by record_id returns same value (pass-through)."""
        result = await client.resolve_document_id(record_id=999)
        assert result == 999

    @pytest.mark.asyncio
    async def test_resolve_multiple_identifiers_raises(self, client):
        """Providing multiple identifiers raises ValueError."""
        with pytest.raises(ValueError, match="exactly one"):
            await client.resolve_document_id(record_id=1, tag="RD-1")

    @pytest.mark.asyncio
    async def test_resolve_no_identifiers_raises(self, client):
        """Providing no identifiers raises ValueError."""
        with pytest.raises(ValueError, match="exactly one"):
            await client.resolve_document_id()

    @pytest.mark.asyncio
    async def test_resolve_nonexistent_tag_raises(self, client):
        """Resolving nonexistent document tag raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            await client.resolve_document_id(tag="RD-99999")

    @pytest.mark.asyncio
    async def test_resolve_nonexistent_number_raises(self, client):
        """Resolving nonexistent document number raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            await client.resolve_document_id(number=99999999)

    @pytest.mark.asyncio
    async def test_resolve_same_document_by_tag_and_number(self, client):
        """Resolving same document by tag and number returns same record_id."""
        doc = DOCUMENTS["test_1"]
        result_by_tag = await client.resolve_document_id(tag=doc["tag"])
        result_by_number = await client.resolve_document_id(number=doc["number"])
        assert result_by_tag == result_by_number
