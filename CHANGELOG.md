# Changelog

All notable changes to the Helix ALM MCP Server project.

## [Unreleased]

### 2025-01-27 - Tag/Number Identifier Support (Issue #6)

**Problem Solved:**
Users see tags like "US-2195" or numbers like "2195" in the Helix ALM UI, but the API requires internal record IDs (e.g., 135). This forced users to somehow discover internal IDs before using tools.

**What Was Implemented:**

1. **Resolver methods in `client.py`:**
   - `resolve_requirement_id(record_id, tag, number)` - Resolves any identifier to internal ID
   - `resolve_document_id(record_id, tag, number)` - Same for documents
   - `search_documents(search, fields, page, per_page)` - POST-based document search (documents API uses POST, not GET like requirements)

2. **Updated tool schemas in `server.py`:**
   - `get_requirement` - Now accepts `record_id`, `tag`, or `number`
   - `update_requirement` - Now accepts `record_id`, `tag`, or `number`
   - `get_document_requirements` - Now accepts `record_id`, `tag`, or `number`

3. **Enhanced tool descriptions:**
   - Clear guidance on which parameter to use when
   - "Provide exactly one of: record_id, tag, or number" in description
   - Detailed parameter descriptions to help AI agents choose correctly

**Technical Decisions:**

- Used `record_id` instead of `id` to avoid confusion with Python's built-in
- Preferred `len([x for x in [...] if x is not None])` over `sum(x is not None...)` for clarity
- Documents API doesn't support `Tag` field in search queries, so resolver extracts number from tag (e.g., "RD-108" → 108) and searches by Number instead

**Test Framework Created:**

- `tests/conftest.py` - Pytest fixtures with proper async client lifecycle
- `tests/fixtures/sample_data.py` - Known test data from Helix ALM export
- `tests/unit/test_resolvers.py` - 18 unit tests for resolver methods
- `tests/integration/test_tools.py` - 17 integration tests for MCP tool handlers
- Added dev dependencies to `pyproject.toml`: pytest, pytest-asyncio, pytest-cov

**Issues Encountered & Fixed:**

1. **Documents API "Tag field does not exist" error** - Documents search API doesn't support Tag field. Fixed by extracting number from tag and searching by Number.

2. **"Event loop is closed" errors** - The `helix_client` singleton in `server.py` kept stale HTTP clients across tests. Fixed by adding `reset_helix_client` fixture that resets `_http_client = None` and `_access_token = None` before each integration test.

3. **Rate limiting (429)** - When running all tests rapidly, hit API rate limits. Tests pass individually and in sequence with the fixture fix.

**Files Created/Modified:**

| File | Change |
|------|--------|
| `src/helix_alm_mcp/client.py` | Added resolver methods, search_documents() |
| `src/helix_alm_mcp/server.py` | Updated tool schemas with new params |
| `tests/conftest.py` | Created - pytest fixtures |
| `tests/fixtures/sample_data.py` | Created - test data |
| `tests/unit/test_resolvers.py` | Created - 18 unit tests |
| `tests/integration/test_tools.py` | Created - 17 integration tests |
| `pyproject.toml` | Added dev dependencies, pytest config |
| `CLAUDE.md` | Updated status, added test commands |

**Test Results:** 35/35 tests passing

---

## Backlog

See `PLANNING.md` for known issues and `BACKLOG.md` for future enhancements.

### Next Priorities

1. **Fix `update_requirement`** (Issue #1) - Wrong payload format, changes don't persist
2. **Implement `add_requirements_to_document`** (Issue #4) - Missing feature critical for demos
