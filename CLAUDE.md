# Helix ALM MCP Server

## Current Status & Next Steps

**Status:** Pre-release - Bug fixes and testing in progress

### Recently Completed

- ✅ **Tag/number identifier support** (Issue #6) - Tools now accept `record_id`, `tag`, or `number`
- ✅ **Fix `update_requirement`** (Issue #1) - Now uses proper field-array payload; returns updated requirement for confirmation
- ✅ **Implement `add_requirements_to_document`** (Issue #4) - Adds requirements to document trees; supports document identifier resolution
- ✅ **Rate-limit handling** - Client retries on HTTP 429 with exponential backoff; inter-test delays prevent rate limiting during pytest
- ✅ **Test suite** - 45 pytest tests (unit + integration) all passing

### Immediate Tasks (Next Session)

1. **Set up GitHub repository** - meaningful commits, .gitignore, README, PR workflow
2. **Eval testing** - tool discovery, tool selection, parameter extraction, multi-model (Promptfoo)
3. **Security hardening** - query injection escaping, SSL verification option, error message sanitization
4. **Test untested tools** - `create_requirement`, `get_requirement_types`, `create_requirement_document`

### Key Files

| File | Purpose |
|------|---------|
| `PLANNING.md` | Testing plan, known issues, pre-release checklist |
| `BACKLOG.md` | Known limitations, future enhancements |
| `src/helix_alm_mcp/server.py` | MCP server with tool definitions |
| `src/helix_alm_mcp/client.py` | Helix ALM REST API client |
| `tests/` | Pytest test suite (45 tests) |

### Running Tests

```bash
# Activate venv and run all tests
source venv/bin/activate && pytest tests/ -v

# Run only unit tests (faster, no API calls for some)
pytest tests/unit/ -v

# Run only integration tests
pytest tests/integration/ -v
```

### API Payload Format (Important!)

The Helix ALM API expects fields as an array with IDs:
```json
{
  "fields": [
    {"id": 2, "label": "Summary", "type": "string", "string": "The value"}
  ]
}
```

Known field IDs:
- 2 = Summary (string)
- 7 = Description (formattedString)

### Item Identifiers (Implemented!)

Helix ALM items have THREE identifiers:
```json
{
  "id": 135,           // Internal record ID (use "record_id" param)
  "number": 3205,      // User-visible item number (use "number" param)
  "tag": "US-3205"     // User-visible tag with prefix (use "tag" param)
}
```

Tools now accept any of these via `record_id`, `tag`, or `number` parameters.
Resolver methods in `client.py`: `resolve_requirement_id()`, `resolve_document_id()`

**Note:** Documents API doesn't support Tag in search queries - resolver extracts number from tag.

---

## Project Overview

A proof-of-concept MCP (Model Context Protocol) server for **Helix ALM** (recently rebranded as **Perforce ALM**). This server enables AI assistants like Claude to interact with Helix ALM for requirements management, issue tracking, and test case management.

## Technology Stack

- **Language**: Python 3.10+
- **MCP Framework**: MCP Python SDK
- **Validation**: Pydantic
- **HTTP Client**: httpx
- **Target**: Prototype/proof-of-concept (not production code)

## Helix ALM Server Configuration

```
Web URL:      https://tryhelixalm.perforce.com
REST API:     https://tryhelixalm.perforce.com:8443/helix-alm/api/v0/
Desktop:      tryhelixalm.perforce.com:99
Project:      Sample Project_8e905741-f4b2-4816-a52a-585bd4dd5464
```

### Swagger UI

Interactive API documentation available at: `https://tryhelixalm.perforce.com:8443/`

## Authentication Flow

Helix ALM uses a two-step authentication process:

1. **Initial Authentication** (one of):
   - **Basic Auth**: `Authorization: Basic {base64(username:password)}`
   - **API Key** (recommended): `Authorization: ApiKey {key}:{secret}`

2. **Get Access Token**:
   - Endpoint: `GET /{projectID}/token`
   - Returns: `{ "tokenType": "Bearer", "accessToken": "...", "expiresOn": "..." }`
   - Token expires in 7 days by default

3. **Use Bearer Token** for all subsequent requests:
   - Header: `Authorization: Bearer {accessToken}`

## REST API Reference

### Base URL Pattern
```
https://{host}:8443/helix-alm/api/v0/{projectID}/{endpoint}
```

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/projects` | GET | List accessible projects (no token required) |
| `/{projectID}/token` | GET | Get access token |
| `/{projectID}/requirements` | GET | List requirements |
| `/{projectID}/requirements/{id}` | GET | Get single requirement |
| `/{projectID}/requirements` | POST | Create requirement |
| `/{projectID}/requirements/{id}` | PUT | Update requirement |
| `/{projectID}/issues` | GET | List issues |
| `/{projectID}/testCases` | GET | List test cases |
| `/{projectID}/configs/fields/{itemType}/customFields` | GET | Get custom fields |
| `/{projectID}/configs/fields/{itemType}/systemFields` | GET | Get system fields |

### Filtering & Search

**Fields Parameter** - Return specific fields only:
```
GET /requirements?fields=Summary,Description,Status
```

**Search Parameter** - Query with criteria:
```
GET /requirements?search=Summary CONTAINS 'login'
GET /requirements?search=Status = 'Approved' AND Priority = 'High'
```

**Search Operators**:
| Operator | Symbol | Example |
|----------|--------|---------|
| EQUALS | `=` | `Status = 'Open'` |
| NOT EQUALS | `!=` | `Status != 'Closed'` |
| CONTAINS | `~` | `Summary ~ 'auth'` |
| CONTAINS (alt) | `CONTAINS` | `Summary CONTAINS 'auth'` |
| IN | `:` | `Folder : 'Requirements'` |
| IN_RECURSE | `:?` | `Folder :? 'Requirements'` |
| GREATER/LESS | `>`, `<`, `>=`, `<=` | `Priority > 3` |

**Logical Operators**: `AND`, `OR`, `NOT` (case-insensitive)

**Pagination**:
```
GET /requirements?page=1&per_page=50
```

**Note**: URL-encode special characters in search queries. Field names with spaces need single quotes: `'Has Attachments'`

## Implementation Status

### Phase 1: Requirements (Current - MVP)

| Tool | Status | Notes |
|------|--------|-------|
| `list_requirements` | ✅ Tested | Works, has pagination |
| `get_requirement` | ✅ Tested | Accepts record_id/tag/number |
| `create_requirement` | ✅ Implemented | Needs testing |
| `update_requirement` | ✅ Fixed | Uses proper field-array format, returns updated requirement |
| `search_requirements` | ✅ Tested | Works |
| `get_requirement_types` | ✅ Implemented | Needs testing |
| `list_requirement_documents` | ✅ Tested | Works |
| `get_document_requirements` | ✅ Tested | Accepts record_id/tag/number |
| `create_requirement_document` | ✅ Implemented | Needs testing |
| `add_requirements_to_document` | ✅ Implemented | Adds reqs to document tree (top level) |

### Phase 2-4: Future (See BACKLOG.md)

Issues, Test Cases, Reports, and Workflows are out of scope for the initial release.

## API Payload Formats (Verified)

### Document Trees - Add Requirements
```
POST /{projectID}/documentTrees/{document_id}/nodes
Payload: {"nodesData": [{"requirementID": <id>}, ...]}
```

### Requirements - Create
```
POST /{projectID}/requirements
Payload: {"requirements": [{"requirementType": {"id": <typeID>}, "fields": [...]}]}
```

### Requirements - Update
```
PUT /{projectID}/requirements/{id}
Payload: {"fields": [{"id": 2, "label": "Summary", "type": "string", "string": "value"}, ...]}
```

### Rate-Limit Handling
- Client automatically retries on HTTP 429 with exponential backoff
- Configurable via `RATE_LIMIT_RETRY_MAX` (default: 5) and `RATE_LIMIT_RETRY_DELAY` (default: 1.0s)
- Tests use `TEST_INTER_REQUEST_DELAY` (default: 1.0s) between API calls

## Project Structure

```
HelixALM_MCP_Server/
├── CLAUDE.md                   # This file - project context for AI
├── PLANNING.md                 # Known issues, test plans
├── BACKLOG.md                  # Future enhancements
├── pyproject.toml              # Project config, dependencies
├── src/
│   └── helix_alm_mcp/
│       ├── __init__.py
│       ├── server.py           # MCP server entry point
│       ├── client.py           # Helix ALM REST API client
│       └── config.py           # Settings from environment
├── tests/
│   ├── conftest.py             # Pytest fixtures
│   ├── fixtures/
│   │   └── sample_data.py      # Test data from Helix ALM
│   ├── unit/
│   │   └── test_resolvers.py   # Unit tests for resolvers
│   └── integration/
│       └── test_tools.py       # Integration tests for MCP tools
└── .env                        # Environment variables (not in git)
```

## Environment Variables

```bash
HELIX_ALM_API_URL=https://tryhelixalm.perforce.com:8443/helix-alm/api/v0
HELIX_ALM_PROJECT=<PROJECT_NAME>
HELIX_ALM_USERNAME=<username>
HELIX_ALM_PASSWORD=<password>
# OR for API Key auth (recommended):
HELIX_ALM_API_KEY=<key>
HELIX_ALM_API_SECRET=<secret>
```

## Documentation Links

- [Helix ALM REST API Guide (Current)](https://help.perforce.com/helix-alm/helixalm/current/restapi/Content/RESTAPI/home-halm-rest-api.htm)
- [Helix ALM REST API 2025.2.0](https://help.perforce.com/helix-alm/helixalm/2025.2.0/rest-api/index.html)
- [Authentication Guide](https://help.perforce.com/helix-alm/helixalm/current/restapi/Content/RESTAPI/AuthorizationSecurity.htm)
- [Filtering Guide (Mecomis)](https://dev.to/mecomis/working-with-helix-alm-rest-api-part-2-filtering-23i6)
- [Python Example Code](https://ftp.perforce.com/alm/helixalm/extras/restapiexamples/HelixALMRestAPIExample.py)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)

## Development Notes

- This is a **prototype**, not production code
- Focus on functionality over error handling initially
- The REST API uses self-signed certificates by default - may need to disable SSL verification for testing
- Requirements have simpler structure than Issues in Helix ALM
- Field names are case-insensitive in search/filter parameters
- The API is otherwise case-sensitive

## MCP Client Compatibility

This server targets all MCP-compatible clients:
- Claude Desktop
- Claude Code
- Other MCP clients

Using `stdio` transport ensures compatibility with all clients.
