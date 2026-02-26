# Helix ALM MCP Server

A Model Context Protocol (MCP) server for Helix ALM (Perforce ALM).

## Quick Start

```bash
# Create virtual environment and install
python3 -m venv venv
source venv/bin/activate
pip install -e .

# Configure credentials
# Edit .env with your API key and secret

# Test the connection
python test_connection.py

# Run the server
helix-alm-mcp
```

## Claude Desktop Configuration

Add to your Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "helix-alm": {
      "command": "/path/to/your/HelixALM_MCP_Server/venv/bin/python",
      "args": ["-m", "helix_alm_mcp.server"],
      "cwd": "/path/to/your/HelixALM_MCP_Server"
    }
  }
}
```

Replace `/path/to/your/HelixALM_MCP_Server` with the actual path where you cloned this repository.

**For Claude Code (VS Code extension or CLI):** A `.mcp.json` file in the project root is also supported. Copy the provided example and update the paths:

```bash
cp .mcp.json.example .mcp.json
# then edit .mcp.json and replace /path/to/your/HelixALM_MCP_Server with your actual path
```

## Available Tools

**Requirements**
- `list_requirements` - List requirements with optional filtering and pagination
- `get_requirement` - Get a single requirement by ID, tag (e.g. `US-2195`), or number
- `create_requirement` - Create a new requirement
- `update_requirement` - Update an existing requirement
- `search_requirements` - Search using Helix ALM query syntax
- `get_requirement_types` - List available requirement types

**Requirement Documents**
- `list_requirement_documents` - List all requirement documents
- `get_document_requirements` - Get requirements in a document
- `create_requirement_document` - Create a new requirement document
- `add_requirements_to_document` - Add requirements to a document

## Search Syntax Examples

```
Summary CONTAINS 'login'
Status = 'Approved'
Priority = 'High' AND Status != 'Closed'
```

See [BACKLOG.md](BACKLOG.md) for known limitations and planned enhancements.

## Known Limitations

This is a proof-of-concept with intentional limitations. See [BACKLOG.md](BACKLOG.md) for the full list of current limitations and planned enhancements.
