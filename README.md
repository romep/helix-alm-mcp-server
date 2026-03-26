# Helix ALM MCP Server

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)

Connect AI assistants to Helix ALM for requirements management through the Model Context Protocol.

## Overview

The [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) is an open standard that lets AI assistants interact with external tools and data sources. This server implements MCP for **Helix ALM** (Perforce ALM), enabling Claude and other MCP-compatible assistants to create, read, update, and search requirements and requirement documents — directly from a conversation.

Instead of switching between your AI assistant and the Helix ALM UI, you can manage requirements through natural language while Helix ALM remains the system of record.

> **Note:** This is a proof-of-concept focused on the **Requirements module**. It intentionally omits destructive operations (no deletes) and does not yet cover Issues or Test Cases. See [Known Limitations](#known-limitations) for details.

## What You Can Do

**Search and browse requirements:**
> *"Show me the high-priority approved requirements"*
>
> Claude calls `search_requirements` with the query `Priority = 'High' AND Status = 'Approved'` and returns a paginated list.

**Create a document with requirements from a PRD:**
> *"Create a PRD called 'Login Redesign' and add three user stories for the authentication flow"*
>
> Claude calls `create_requirement_document`, then `create_requirement` three times, then `add_requirements_to_document` to link them all together.

**Look up a requirement by its tag:**
> *"What are the details of US-2195?"*
>
> Claude calls `get_requirement` with `tag="US-2195"` and returns the full requirement with all fields.

## Prerequisites

- **Python 3.10** or later
- **Helix ALM server** with REST API enabled (port 8443 by default)
- **API Key credentials** (recommended) or username/password for your Helix ALM server
- **An MCP client**: [Claude Desktop](https://claude.ai/download), [Claude Code](https://docs.anthropic.com/en/docs/claude-code), or any MCP-compatible client
- **git** (to clone the repository)

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/romep/helix-alm-mcp-server.git
cd helix-alm-mcp-server
```

### 2. Create a virtual environment and install

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

### 3. Configure credentials

```bash
cp .env.example .env
```

Edit `.env` with your Helix ALM connection details:

- **`HELIX_ALM_API_URL`** — Your server's REST API URL (e.g., `https://your-server:8443/helix-alm/api/v0`)
- **`HELIX_ALM_PROJECT`** — Project name with UUID (found in Helix ALM admin settings)
- **`HELIX_ALM_API_KEY`** and **`HELIX_ALM_API_SECRET`** — API key credentials (recommended), or use `HELIX_ALM_USERNAME` / `HELIX_ALM_PASSWORD` for basic auth

See [Configuration Reference](#configuration-reference) for all available options.

### 4. Test the connection

```bash
python test_connection.py
```

This script authenticates with your Helix ALM server, lists a few requirements, fetches requirement types, and lists documents. If everything is configured correctly, you'll see `ALL TESTS PASSED`.

### 5. Configure your MCP client

See the next section for setup instructions for Claude Desktop, Claude Code, or other clients.

## MCP Client Configuration

### Claude Desktop

Add to your Claude Desktop config file:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "helix-alm": {
      "command": "/path/to/helix-alm-mcp-server/venv/bin/python",
      "args": ["-m", "helix_alm_mcp.server"],
      "cwd": "/path/to/helix-alm-mcp-server"
    }
  }
}
```

Replace `/path/to/helix-alm-mcp-server` with the actual path where you cloned the repository. **Restart Claude Desktop** after changing the config.

### Claude Code (VS Code extension or CLI)

Copy the provided example and update the paths:

```bash
cp .mcp.json.example .mcp.json
# Edit .mcp.json and replace /path/to/your/HelixALM_MCP_Server with your actual path
```

Claude Code automatically detects `.mcp.json` in the project root.

### Other MCP Clients

Any client supporting the MCP stdio transport can use this server. Point it at the `helix-alm-mcp` entry point or run `python -m helix_alm_mcp.server` from the project directory.

## Available Tools

### Requirements

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `list_requirements` | List requirements with filtering and pagination | `search`, `fields`, `page`, `per_page` |
| `get_requirement` | Get a single requirement by ID, tag, or number | `record_id` or `tag` or `number` |
| `create_requirement` | Create a new requirement | `summary` (required), `description`, `requirement_type` |
| `update_requirement` | Update a requirement's summary and/or description | identifier + `summary` and/or `description` |
| `search_requirements` | Search with Helix ALM query syntax | `query` (required), `fields`, `page`, `per_page` |
| `get_requirement_types` | List all available requirement types | *(none)* |

### Requirement Documents

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `list_requirement_documents` | List documents with filtering and pagination | `search`, `fields`, `page`, `per_page` |
| `get_document_requirements` | Get requirements within a document | identifier + `page`, `per_page` |
| `create_requirement_document` | Create a new document | `name` (required), `description`, `document_type` |
| `add_requirements_to_document` | Add existing requirements to a document | identifier + `requirement_ids` array |

<details>
<summary><strong>Item Identifiers</strong></summary>

Helix ALM items have three types of identifiers. Tools that reference a specific item accept any one of these:

| Parameter | Example | When to Use |
|-----------|---------|-------------|
| `tag` | `"US-2195"`, `"RD-108"` | When referencing items as shown in the Helix ALM UI |
| `number` | `2195`, `108` | When referencing just the numeric portion |
| `record_id` | `135` | When using IDs returned from API calls (e.g., after `create_requirement`) |

Provide exactly one identifier per call. The server resolves tags and numbers to internal IDs automatically.

</details>

## Search Syntax

Use the `search` parameter (on `list_requirements`, `list_requirement_documents`) or the `query` parameter (on `search_requirements`) to filter results using Helix ALM query syntax.

**Examples:**

```
Summary CONTAINS 'login'
Status = 'Approved'
Priority = 'High' AND Status != 'Closed'
```

**Operators:**

| Operator | Symbol | Example |
|----------|--------|---------|
| Equals | `=` | `Status = 'Open'` |
| Not Equals | `!=` | `Status != 'Closed'` |
| Contains | `CONTAINS` | `Summary CONTAINS 'auth'` |
| Greater / Less Than | `>`, `<`, `>=`, `<=` | `Priority > 3` |
| In Folder | `:` | `Folder : 'Requirements'` |
| In Folder (recursive) | `:?` | `Folder :? 'Requirements'` |

**Logical operators:** `AND`, `OR`, `NOT` (case-insensitive)

## Architecture

```
MCP Client (Claude)  <── stdio ──>  MCP Server (server.py)  <── HTTPS ──>  Helix ALM REST API
                                          |
                                     client.py (API client)
                                     config.py (settings)
```

- **`server.py`** — Registers 10 MCP tools and handles tool dispatch. Uses the [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) with stdio transport for compatibility with all MCP clients.
- **`client.py`** — Wraps the Helix ALM REST API. Handles authentication (API key or basic auth to bearer token exchange), rate-limit retries with exponential backoff, and identifier resolution (tag/number to internal ID).
- **`config.py`** — Loads settings from environment variables via Pydantic Settings. Contains named constants for field IDs, type mappings, and pagination defaults.

## Configuration Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `HELIX_ALM_API_URL` | Yes | REST API base URL | `https://your-server:8443/helix-alm/api/v0` |
| `HELIX_ALM_PROJECT` | Yes | Project name with UUID | `My Project_abc123-def456-...` |
| `HELIX_ALM_API_KEY` | Yes* | API key for authentication | *(from Helix ALM admin)* |
| `HELIX_ALM_API_SECRET` | Yes* | API secret for authentication | *(from Helix ALM admin)* |
| `HELIX_ALM_USERNAME` | Alt* | Username for basic auth | `admin` |
| `HELIX_ALM_PASSWORD` | Alt* | Password for basic auth | |
| `RATE_LIMIT_RETRY_MAX` | No | Max retries on HTTP 429 (default: 5) | `5` |
| `RATE_LIMIT_RETRY_DELAY` | No | Initial backoff delay in seconds (default: 1.0) | `1.0` |

\* Provide **either** API Key + Secret (recommended) **or** Username + Password.

## Troubleshooting

**"SSL certificate verify failed"**
Expected with self-signed certificates, which are common in Helix ALM deployments. SSL verification is disabled by default in this proof-of-concept. Ensure your `HELIX_ALM_API_URL` is correct.

**"Error: HELIX_ALM_PROJECT not configured"**
The `.env` file is missing or the `HELIX_ALM_PROJECT` variable is empty. Run `cp .env.example .env` and fill in your values.

**"Error: No authentication configured"**
Neither API key nor basic auth credentials are set in `.env`. Provide either `HELIX_ALM_API_KEY` + `HELIX_ALM_API_SECRET` or `HELIX_ALM_USERNAME` + `HELIX_ALM_PASSWORD`.

**Rate limiting (HTTP 429)**
The server automatically retries with exponential backoff (up to 5 attempts by default). If you hit persistent 429 errors, your Helix ALM server may have strict rate limits — check with your server administrator.

**Tools not appearing in Claude**
For Claude Desktop, restart the application after changing the config. For Claude Code, ensure `.mcp.json` is in the project root and the Python executable path is correct.

**Connection test passes but Claude can't use tools**
Verify the `cwd` path in your MCP client config matches the project directory so that the `.env` file is found at runtime.

**404 on token endpoint or "No Projects Available"**
If you're using the Perforce trial server (`tryhelixalm.perforce.com`), the server is periodically reset — projects and API keys are wiped. You'll need to re-register for a new trial instance and update your `.env` with the new project name, UUID, and credentials. To verify, visit the Swagger UI at `https://tryhelixalm.perforce.com:8443/` and check if your project appears in the project selector.

## Development

### Project Structure

```
helix-alm-mcp-server/
├── src/helix_alm_mcp/
│   ├── server.py           # MCP tool definitions and dispatch
│   ├── client.py           # Helix ALM REST API client
│   ├── config.py           # Settings and named constants
│   └── models.py           # Pydantic type hints
├── tests/
│   ├── unit/               # Deterministic resolver tests
│   ├── integration/        # Live API tests
│   ├── fixtures/           # Known test data
│   └── conftest.py         # Shared fixtures
├── promptfooconfig.yaml    # Direct MCP eval tests
├── promptfoo-llm.yaml      # LLM eval tests
├── test_connection.py      # Quick connectivity check
├── .env.example            # Configuration template
└── .mcp.json.example       # MCP client config template
```

### Running Tests

```bash
source venv/bin/activate

# All tests (58 total: 18 unit + 40 integration)
pytest tests/ -v

# Unit tests only (fast, no API calls)
pytest tests/unit/ -v

# Integration tests only (requires valid .env credentials, hits real API)
pytest tests/integration/ -v
```

Integration tests include a built-in delay between API calls to avoid rate limiting.

### Eval Testing with Promptfoo

The project uses [Promptfoo](https://www.promptfoo.dev/) for evaluating MCP tool behavior at two levels:

**Direct MCP tests** (`promptfooconfig.yaml`) — 10 tests that call MCP tools directly and assert on responses. No LLM needed, fully deterministic, zero cost.

```bash
promptfoo eval
```

**LLM tool-selection tests** (`promptfoo-llm.yaml`) — 16 tests that give an LLM a natural-language prompt and verify it selects the right tool with correct parameters. Covers tool discovery, parameter extraction, pagination follow-through, and anti-hallucination (verifying the LLM doesn't claim capabilities the server doesn't have).

```bash
promptfoo eval -c promptfoo-llm.yaml
```

Some assertions use `llm-rubric` — semantic evaluation by an LLM — for cases where string matching can't distinguish nuance (e.g., "you can delete" vs. "deletion is not supported"). All LLM eval tests run against a locally-hosted model via [Ollama](https://ollama.ai/) (qwen2.5:32b), keeping costs at zero.

```bash
# View results in the Promptfoo dashboard
promptfoo view
```

## Known Limitations

This is a proof-of-concept with intentional limitations:

- **Requirements module only** — Issues and Test Cases are not yet supported
- **No delete operations** — intentional safety decision to prevent accidental data loss
- **Updates limited to Summary and Description** — other fields must be edited in the Helix ALM UI
- **Document structure is flat** — requirements are added to the top level only (no hierarchy)
- **SSL verification disabled** — acceptable for PoC and internal deployments, should be configurable for production

See [BACKLOG.md](BACKLOG.md) for the complete list of 13 documented limitations with workarounds and planned enhancements.

## Roadmap

- Security hardening — SSL verification option, query injection escaping, error message sanitization
- Issues module — list, get, create, update, and search issues
- Test Cases module — list, get, manage test runs

## Contributing

Contributions are welcome! Please:

1. Open an issue to discuss your proposed change before submitting a PR
2. Fork the repo and create a feature branch
3. Run `pytest tests/ -v` to verify all tests pass
4. Follow existing code patterns in `server.py` and `client.py`

## License

MIT License — see [LICENSE](LICENSE) for details.

## Acknowledgments

- [Perforce](https://www.perforce.com/) for Helix ALM and the REST API
- [Anthropic](https://www.anthropic.com/) for the Model Context Protocol
- Built with the [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
