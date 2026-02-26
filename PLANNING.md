# Helix ALM MCP Server - Pre-Release Planning Document

**Created:** January 21, 2026
**Purpose:** Track testing, issues, and polish work before GitHub publication
**Status:** In Progress

---

## Quick Start for New Sessions

**Read these files first:**
1. This file (PLANNING.md) - Testing plan, known issues, next actions
2. CLAUDE.md - Project overview, implementation status, code snippets for next tasks
3. BACKLOG.md - Known limitations and future enhancements

**Immediate priorities:**
1. ~~Add support for tag/number identifiers (Issue #6)~~ ✅ Done
2. ~~Fix `update_requirement` bug in `client.py` (Issue #1)~~ ✅ Done
3. ~~Implement `add_requirements_to_document` tool (Issue #4)~~ ✅ Done
4. Set up GitHub repo, eval testing, security review

**Key files to modify:**
- `src/helix_alm_mcp/client.py` - REST API client methods
- `src/helix_alm_mcp/server.py` - MCP tool definitions

---

## Table of Contents

1. [Project Goals](#project-goals)
2. [Core Use Cases](#core-use-cases)
3. [Known Issues](#known-issues)
4. [Testing Plan](#testing-plan)
5. [Missing Functionality](#missing-functionality)
6. [Usability & Scaling](#usability--scaling)
7. [Pre-Release Checklist](#pre-release-checklist)
8. [Test Results Log](#test-results-log)

---

## Project Goals

Demonstrate a proof-of-concept MCP server for Helix ALM that enables AI assistants to:

1. **CRUD for Requirements** - Create, read, update, delete requirements
2. **CRUD for Requirement Documents** - Create, read, update, delete requirement documents
3. **Document Management** - Add/remove requirements from documents
4. **End-to-End Demo** - Parse a markdown PRD → Create requirement document → Create requirements → Add them to the document

---

## Core Use Cases

### Use Case 1: Requirements CRUD
| Operation | Tool | Status | Notes |
|-----------|------|--------|-------|
| List requirements | `list_requirements` | ✅ Tested | Works with pagination |
| Get single requirement | `get_requirement` | ✅ Tested | Works |
| Create requirement | `create_requirement` | ⚠️ Untested | Needs verification |
| Update requirement | `update_requirement` | ✅ Fixed | Uses field-array format, returns updated req |
| Delete requirement | - | ❌ Not implemented | Not in scope for PoC |

### Use Case 2: Requirement Documents CRUD
| Operation | Tool | Status | Notes |
|-----------|------|--------|-------|
| List documents | `list_requirement_documents` | ✅ Tested | Works but verbose |
| Get single document | - | ⚠️ Partial | Via `get_document_requirements` |
| Create document | `create_requirement_document` | ⚠️ Untested | Needs verification |
| Update document | - | ❌ Not implemented | Not in scope for PoC |
| Delete document | - | ❌ Not implemented | Not in scope for PoC |

### Use Case 3: Document-Requirement Association
| Operation | Tool | Status | Notes |
|-----------|------|--------|-------|
| Get requirements in document | `get_document_requirements` | ✅ Tested | Works |
| Add requirement to document | `add_requirements_to_document` | ✅ Implemented | Adds to document tree top level |
| Remove requirement from document | - | ❌ Not implemented | Not in scope for PoC |

### Use Case 4: Search & Discovery
| Operation | Tool | Status | Notes |
|-----------|------|--------|-------|
| Search requirements | `search_requirements` | ✅ Tested | Works (uses list_requirements internally) |
| Get requirement types | `get_requirement_types` | ⚠️ Untested | Needs verification |

---

## Known Issues

### Issue #1: Update Requirement Does Not Persist (Critical)

**Status:** ✅ Fixed (Feb 25, 2026)
**Severity:** Critical
**First Reported:** January 21, 2026

**Problem:** The `update_requirement` tool returns `{}` but changes are not persisted.

**Root Cause Analysis:**
Looking at `client.py:196-198`, the update sends:
```python
async def update_requirement(self, requirement_id: int, data: dict) -> dict:
    return await self.put(f"requirements/{requirement_id}", data)
```

But the Helix ALM API expects the same field structure as create:
```json
{
  "fields": [
    {"id": 2, "label": "Summary", "type": "string", "string": "New value"}
  ]
}
```

**Fix Required:** Rewrite `update_requirement` to use proper field format with field IDs.

---

### Issue #2: Insufficient Feedback on Update Operations (Medium)

**Status:** ✅ Fixed (Feb 25, 2026) - Fixed alongside Issue #1
**Severity:** Medium

**Problem:** Update operations return `{}` regardless of success/failure.

**Fix:** `update_requirement` now fetches and returns the updated requirement after PUT.

---

### Issue #3: Verbose Responses for List Operations (Low)

**Status:** 🟡 Open
**Severity:** Low

**Problem:** `list_requirement_documents` returns all fields, creating large responses.

**Fix Required:** Add `fields` parameter support like `list_requirements` has.

---

### Issue #4: Missing "Add Requirements to Document" Tool (Critical)

**Status:** ✅ Fixed (Feb 25, 2026)
**Severity:** Critical - Blocks core use case

**Problem:** No way to add requirements to a requirement document.

**API Endpoint Available:**
```
POST /{projectID}/documentTrees/{itemID}/nodes
```

This adds existing requirements as nodes in a requirement document tree.

**Implementation:** See CLAUDE.md for the complete code to add.

**Design Decision:** Single tool `add_requirements_to_document` accepts an array of requirement IDs:
- For single requirement: `requirement_ids=[123]`
- For multiple: `requirement_ids=[123, 124, 125]`
- All requirements added to top level (hierarchy support is in BACKLOG.md)

---

### Issue #5: No Pagination Guidance in Tool Descriptions (Medium)

**Status:** 🟡 Open
**Severity:** Medium

**Problem:** LLMs may request all requirements at once, overwhelming context windows.

**Fix Required:** Update tool descriptions in `server.py`. Ready-to-use description text is in CLAUDE.md under "Tool Description Updates".

---

### Issue #6: Tools Only Accept Internal IDs, Not User-Visible Tags/Numbers (Critical)

**Status:** ✅ Fixed (Feb 25, 2026)
**Severity:** Critical - Major usability issue

**Problem:** All tools currently require the internal `id` field, but users only see `tag` (e.g., "US-2195") or `number` (e.g., 2195) in the Helix ALM UI.

**Helix ALM Identifier Types:**
```json
{
  "id": 135,           // Internal record ID (used by API endpoints)
  "number": 3205,      // User-visible item number
  "tag": "US-3205"     // User-visible tag with prefix (US-, RD-, FR-, etc.)
}
```

**API Behavior (Confirmed from docs):**
- Direct endpoints like `GET /requirements/{itemID}` require internal `id` (integer)
- Search endpoints accept queries like `search="Tag = 'US-2195'"` or `search="Number = 3205"`

**Recommended Solution:** Accept multiple identifier types in tool parameters:

```python
# Example for get_requirement
async def get_requirement(
    id: int | None = None,        # Internal ID (for programmatic use after create)
    tag: str | None = None,       # User-visible tag like "US-2195"
    number: int | None = None     # User-visible number like 2195
) -> dict:
    """Get a requirement by ID, tag, or number. Provide exactly one identifier."""
```

**Implementation approach:**
1. Add a helper method in `client.py` to resolve tag/number → internal ID via search
2. Update all tools that take item identifiers to accept `id`, `tag`, or `number`
3. Validate that exactly one identifier is provided
4. For tag/number, do a search lookup first, then use the internal ID for the actual operation

**Helper method to add:**
```python
async def resolve_requirement_id(
    self,
    id: int | None = None,
    tag: str | None = None,
    number: int | None = None,
) -> int:
    """Resolve a requirement identifier to internal ID.

    Accepts internal id, user-visible tag, or user-visible number.
    Returns the internal ID for use with API endpoints.
    Raises ValueError if item not found or multiple identifiers provided.
    """
    # Count provided identifiers
    provided = sum(x is not None for x in [id, tag, number])
    if provided != 1:
        raise ValueError("Provide exactly one of: id, tag, or number")

    if id is not None:
        return id

    # Search by tag or number
    if tag is not None:
        search_query = f"Tag = '{tag}'"
    else:
        search_query = f"Number = {number}"

    result = await self.list_requirements(search=search_query, per_page=1)
    requirements = result.get("requirements", [])

    if not requirements:
        raise ValueError(f"Requirement not found: {tag or number}")

    return requirements[0]["id"]
```

**Tools affected:**
- `get_requirement` - needs id/tag/number params
- `update_requirement` - needs id/tag/number params
- `add_requirements_to_document` - requirement_ids array (keep as IDs for efficiency, document in description)
- `get_document_requirements` - document_id param
- Other document tools

**Trade-off for `add_requirements_to_document`:**
For batch operations, requiring internal IDs avoids N extra API calls. The tool description should clarify:
- When creating new requirements, use the returned IDs directly
- When referencing existing requirements by tag, look them up first with `get_requirement(tag="US-123")`

---

## Testing Plan

### Phase 1: Verify Existing Tools (Individual)

Run each tool and record results:

| # | Tool | Test Case | Expected Result | Actual Result | Status |
|---|------|-----------|-----------------|---------------|--------|
| 1.1 | `list_requirements` | List first 10 | Returns array of requirements | | ⬜ |
| 1.2 | `list_requirements` | Search by summary | Returns filtered results | | ⬜ |
| 1.3 | `get_requirement` | Get known ID (2204) | Returns requirement details | | ⬜ |
| 1.4 | `create_requirement` | Create "Test Req" | Returns new requirement with ID | | ⬜ |
| 1.5 | `update_requirement` | Update summary | Summary changes persist | | ⬜ |
| 1.6 | `search_requirements` | Query "CONTAINS 'test'" | Returns matching requirements | | ⬜ |
| 1.7 | `get_requirement_types` | List all types | Returns type array | | ⬜ |
| 1.8 | `list_requirement_documents` | List all docs | Returns document array | | ⬜ |
| 1.9 | `get_document_requirements` | Get doc 108 reqs | Returns requirements in doc | | ⬜ |
| 1.10 | `create_requirement_document` | Create "Test Doc" | Returns new document with ID | | ⬜ |

### Phase 2: End-to-End Workflow

| # | Scenario | Steps | Status |
|---|----------|-------|--------|
| 2.1 | Create document with requirements | 1. Create document<br>2. Create requirements<br>3. Add requirements to document<br>4. Verify document contents | ⬜ |
| 2.2 | Markdown PRD → Helix ALM | 1. Parse sample PRD<br>2. Extract requirements<br>3. Create document<br>4. Create requirements<br>5. Add to document | ⬜ |

### Phase 3: Edge Cases & Error Handling

| # | Test Case | Expected Behavior | Status |
|---|-----------|-------------------|--------|
| 3.1 | Invalid requirement ID | Clear error message | ⬜ |
| 3.2 | Empty search results | Empty array, no error | ⬜ |
| 3.3 | Invalid search syntax | Helpful error message | ⬜ |
| 3.4 | Rate limiting | Appropriate retry message | ⬜ |

---

## Missing Functionality

### Critical (Must Have for Demo)

1. ~~**`add_requirements_to_document`**~~ ✅ Implemented (Feb 25, 2026)
   - API: `POST /{projectID}/documentTrees/{itemID}/nodes`
   - Payload: `{"nodesData": [{"requirementID": <reqID>}, ...]}`

2. ~~**Fix `update_requirement`**~~ ✅ Fixed (Feb 25, 2026)

### Nice to Have

3. **`get_requirement_document`** - Get single document by ID (cleaner than current approach)

4. **`remove_requirement_from_document`** - Remove requirement from document tree

5. **Summary/compact mode** for list operations

---

## Usability & Scaling

### The Problem

Helix ALM projects can contain thousands of requirements accumulated over years. Current behavior:
- `list_requirements` defaults to 50 items per page (good)
- `list_requirement_documents` returns all fields (verbose)
- No guidance to LLMs about pagination or filtering

### MCP Best Practices for Large Data Sets

**1. Smart Defaults**
- Default to small page sizes (10-25 items)
- Return summary fields by default, full details on request
- Include pagination metadata in responses

**2. Tool Descriptions Should Guide LLM Behavior**
- Explicitly mention pagination in descriptions
- Suggest filtering strategies
- Warn about large result sets

**3. Response Structure**
```json
{
  "items": [...],
  "paging": {
    "page": 1,
    "per_page": 25,
    "total_items": 1547,
    "total_pages": 62,
    "has_more": true
  },
  "hint": "Use 'search' parameter to filter results. Example: search=\"Status = 'Approved'\""
}
```

**4. Implement "Summary" vs "Full" Modes**
- Summary: ID, tag, summary, status, type
- Full: All fields including description, history, etc.

### Recommended Changes

| Change | Priority | Effort |
|--------|----------|--------|
| Reduce default page size to 25 | High | Low |
| Add summary mode for requirements | Medium | Medium |
| Add fields param to document listing | Medium | Low |
| Add pagination hints to responses | Medium | Low |
| Update tool descriptions with guidance | High | Low |

---

## Pre-Release Checklist

### Code Quality
- [ ] All tools tested and working
- [ ] Error messages are helpful
- [ ] No hardcoded test values
- [ ] SSL verification can be configured
- [ ] Environment variables documented

### Documentation
- [ ] README.md is complete and accurate
- [ ] CLAUDE.md updated with final tool list
- [ ] Installation instructions tested
- [ ] Example usage documented
- [ ] Known limitations documented

### Repository Setup
- [ ] .gitignore covers sensitive files
- [ ] .env.example provided
- [ ] LICENSE file added
- [ ] No credentials in code or history

### Demo Ready
- [ ] End-to-end workflow works
- [ ] Sample PRD markdown prepared
- [ ] Screen recording or walkthrough possible

---

## Test Results Log

### Session: [Date TBD]

```
Tool: list_requirements
Input: {"per_page": 5}
Result: [Record result here]
Status: ⬜
```

---

## Issue Tracking Options

For ongoing development, consider:

1. **GitHub Issues** - Standard, integrates with repo
2. **This Document** - Simple, single source of truth for PoC
3. **Helix ALM Issues** - Dog-food our own tool (advanced)
4. **Linear** - Modern issue tracking

**Recommendation for PoC:** Keep using this document. Migrate to GitHub Issues after publication.

---

## Next Actions

1. [x] ~~Add tag/number identifier support (Issue #6)~~ ✅ Done
2. [x] ~~Fix `update_requirement` field format (Issue #1)~~ ✅ Done
3. [x] ~~Implement `add_requirements_to_document` tool (Issue #4)~~ ✅ Done
4. [x] ~~Add rate-limit handling (client retry + test delays)~~ ✅ Done
5. [ ] Run Phase 1 tests (see Testing Plan above) - partially done via pytest (45 tests passing)
6. [ ] Update tool descriptions with pagination guidance (Issue #5)
7. [ ] Run end-to-end demo (Use Case 2.2)
8. [ ] Set up GitHub repository
9. [ ] Eval testing (Promptfoo)
10. [ ] Security review
11. [ ] Prepare README for GitHub
12. [ ] Final documentation pass (sync CLAUDE.md, README.md, BACKLOG.md)

---

## Session Log

### January 21, 2026 - Session 1
- Created PLANNING.md with testing plan and issue tracking
- Created BACKLOG.md with known limitations and future enhancements
- Updated CLAUDE.md with current status and next steps
- Added README.md link to BACKLOG.md
- Identified root cause of update_requirement bug (wrong payload format)
- Documented add_requirements_to_document API and design decision
- Added workflow guidance to add_requirements_to_document tool description
- Added pagination guidance text for list tool descriptions
- **Discovered critical Issue #6:** Tools only accept internal IDs, but users see tags/numbers
  - API confirmed to require internal ID for direct endpoints
  - Can use search to resolve tag/number → ID
  - Added resolver helper code and updated priorities

**Handoff to next session:**
1. Start with Issue #6 (tag/number support) - it affects all tools
2. Then fix update_requirement (Issue #1)
3. Then add add_requirements_to_document (Issue #4)
4. All code snippets ready in PLANNING.md (Issue #6) and CLAUDE.md

### February 25, 2026 - Session 2
- **Rate-limit handling:** Added exponential backoff retry to `client.py` `_request` and `authenticate` methods. Added configurable constants to `config.py` (Pydantic Settings). Added inter-test delay fixture to `conftest.py`.
- **Fixed `update_requirement` (Issue #1 + #2):** Rewrote to use proper field-array payload (`{"fields": [...]}`). Now returns the updated requirement after PUT for confirmation.
- **Implemented `add_requirements_to_document` (Issue #4):** Added client method and MCP tool. Discovered correct API payload format differs from docs: `{"nodesData": [{"requirementID": <id>}]}` (not `{"nodes": [{"requirement": {"id": <id>}}]}`).
- **Fixed Issue #6:** Tag/number identifier support already implemented in prior session; verified working.
- **Test suite expanded:** 35 → 45 tests, all passing. Added update persistence tests (summary, description, both), add-requirements tests (single, multiple, tag/number resolution, error cases).
- **Test isolation improvement:** Changed add-requirements tests to create fresh documents per test instead of reusing shared test data.
- **Updated documentation:** CLAUDE.md and PLANNING.md reflect all completed work.

**Handoff to next session:**
1. Set up GitHub repository (meaningful commits, .gitignore, README, PR workflow)
2. Eval testing (tool discovery, tool selection, parameter extraction, multi-model with Promptfoo)
3. Security hardening (query injection escaping, SSL verification option, error message sanitization)
4. Test remaining untested tools: `create_requirement`, `get_requirement_types`, `create_requirement_document`
5. Run end-to-end demo (Use Case 2.2)
6. Open issues: #3 (verbose list responses), #5 (pagination guidance in tool descriptions)

---

*Last Updated: February 25, 2026*
