"""Helix ALM MCP Server - Main entry point."""

import asyncio
import json

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .client import helix_client, format_requirement_summary
from .config import settings


# Create the MCP server
server = Server("helix-alm-mcp")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="list_requirements",
            description="List requirements from Helix ALM with optional filtering and search",
            inputSchema={
                "type": "object",
                "properties": {
                    "search": {
                        "type": "string",
                        "description": "Search query using Helix ALM syntax (e.g., \"Summary CONTAINS 'login'\" or \"Status = 'Approved'\")",
                    },
                    "fields": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific fields to return (e.g., ['Summary', 'Description', 'Status'])",
                    },
                    "page": {
                        "type": "integer",
                        "description": "Page number for pagination (default: 1)",
                        "default": 1,
                    },
                    "per_page": {
                        "type": "integer",
                        "description": "Number of items per page (default: 50, max: 300)",
                        "default": 50,
                    },
                },
            },
        ),
        Tool(
            name="get_requirement",
            description="""Get a single requirement by its identifier. Provide exactly one of: record_id, tag, or number.

- Use 'tag' when the user references a requirement like "US-2195" (visible in Helix ALM UI)
- Use 'number' when the user references just the number like "2195" (visible in Helix ALM UI)
- Use 'record_id' when working with IDs returned from previous API calls (e.g., after create_requirement)""",
            inputSchema={
                "type": "object",
                "properties": {
                    "record_id": {
                        "type": "integer",
                        "description": "Internal record ID returned by API operations like create_requirement. Use this for programmatic workflows.",
                    },
                    "tag": {
                        "type": "string",
                        "description": "User-visible tag with type prefix, e.g., 'US-2195' for User Story, 'FR-100' for Functional Requirement. This is what users see in the Helix ALM interface.",
                    },
                    "number": {
                        "type": "integer",
                        "description": "User-visible item number without prefix, e.g., 2195. This is the numeric portion shown in the Helix ALM interface.",
                    },
                },
            },
        ),
        Tool(
            name="create_requirement",
            description="Create a new requirement in Helix ALM",
            inputSchema={
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "string",
                        "description": "The summary/title of the requirement",
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed description of the requirement (supports HTML formatting)",
                    },
                    "requirement_type": {
                        "type": "string",
                        "description": "Type of requirement to create",
                        "enum": [
                            "User Story",
                            "Task",
                            "Overview",
                            "Functional Requirement",
                            "Business Requirement",
                            "Non-Functional Requirement",
                            "Design Note",
                            "Software  Requirements",
                            "Security Requirement",
                            "Technical Requirement",
                            "Hardware Requirements",
                            "Risk",
                            "Performance Requirement",
                            "Use Case",
                            "Compliance Requirement",
                            "Glossary",
                            "Hazards",
                            "Harms",
                        ],
                        "default": "Functional Requirement",
                    },
                },
                "required": ["summary"],
            },
        ),
        Tool(
            name="update_requirement",
            description="""Update an existing requirement. Provide exactly one identifier (record_id, tag, or number) plus the fields to update.

- Use 'tag' when the user references a requirement like "US-2195" (visible in Helix ALM UI)
- Use 'number' when the user references just the number like "2195" (visible in Helix ALM UI)
- Use 'record_id' when working with IDs returned from previous API calls""",
            inputSchema={
                "type": "object",
                "properties": {
                    "record_id": {
                        "type": "integer",
                        "description": "Internal record ID returned by API operations. Use this for programmatic workflows.",
                    },
                    "tag": {
                        "type": "string",
                        "description": "User-visible tag with type prefix, e.g., 'US-2195'. This is what users see in the Helix ALM interface.",
                    },
                    "number": {
                        "type": "integer",
                        "description": "User-visible item number without prefix, e.g., 2195.",
                    },
                    "summary": {
                        "type": "string",
                        "description": "New summary/title for the requirement",
                    },
                    "description": {
                        "type": "string",
                        "description": "New description for the requirement",
                    },
                },
            },
        ),
        Tool(
            name="search_requirements",
            description="Search requirements using Helix ALM query syntax. Supports operators: = (equals), != (not equals), CONTAINS, >, <, >=, <=. Chain with AND, OR, NOT.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (e.g., \"Summary CONTAINS 'auth' AND Status = 'Approved'\")",
                    },
                    "fields": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific fields to return",
                    },
                    "page": {
                        "type": "integer",
                        "description": "Page number for pagination (default: 1)",
                        "default": 1,
                    },
                    "per_page": {
                        "type": "integer",
                        "description": "Number of items per page (default: 50, max: 300)",
                        "default": 50,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_requirement_types",
            description="Get the list of available requirement types (e.g., Business Requirement, Functional Requirement)",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="list_requirement_documents",
            description="List requirement documents in the project with optional filtering and search",
            inputSchema={
                "type": "object",
                "properties": {
                    "search": {
                        "type": "string",
                        "description": "Search query using Helix ALM syntax (e.g., \"Name CONTAINS 'PRD'\")",
                    },
                    "fields": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific fields to return (e.g., ['Name', 'Description', 'Document Type'])",
                    },
                    "page": {
                        "type": "integer",
                        "description": "Page number for pagination (default: 1)",
                        "default": 1,
                    },
                    "per_page": {
                        "type": "integer",
                        "description": "Number of items per page (default: 25, max: 300)",
                        "default": 25,
                    },
                },
            },
        ),
        Tool(
            name="get_document_requirements",
            description="""Get all requirements in a specific requirement document. Provide exactly one identifier (record_id, tag, or number) for the document.

- Use 'tag' when the user references a document like "RD-108" (visible in Helix ALM UI)
- Use 'number' when the user references just the number like "108" (visible in Helix ALM UI)
- Use 'record_id' when working with IDs returned from previous API calls (e.g., after create_requirement_document)""",
            inputSchema={
                "type": "object",
                "properties": {
                    "record_id": {
                        "type": "integer",
                        "description": "Internal record ID of the document returned by API operations. Use this for programmatic workflows.",
                    },
                    "tag": {
                        "type": "string",
                        "description": "User-visible document tag, e.g., 'RD-108'. This is what users see in the Helix ALM interface.",
                    },
                    "number": {
                        "type": "integer",
                        "description": "User-visible document number without prefix, e.g., 108.",
                    },
                    "page": {
                        "type": "integer",
                        "description": "Page number for pagination (default: 1)",
                        "default": 1,
                    },
                    "per_page": {
                        "type": "integer",
                        "description": "Number of items per page (default: 50)",
                        "default": 50,
                    },
                },
            },
        ),
        Tool(
            name="create_requirement_document",
            description="Create a new requirement document in Helix ALM",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the requirement document",
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional description of the document",
                    },
                    "document_type": {
                        "type": "string",
                        "description": "Document type: 'PRD' (default), 'MRD', 'FMEA', or 'EPIC'",
                        "enum": ["PRD", "MRD", "FMEA", "EPIC"],
                        "default": "PRD",
                    },
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="add_requirements_to_document",
            description="""Add one or more existing requirements to a requirement document.

Requirements are added to the top level of the document tree.
Provide exactly one document identifier (record_id, tag, or number).

Common workflow for importing a PRD into Helix ALM:
1. Create the document with create_requirement_document
2. Create each requirement with create_requirement (collect the returned IDs)
3. Add all requirements to the document with this tool using the collected IDs

Example: After creating requirements with IDs [101, 102, 103], call this tool with
document number=50 and requirement_ids=[101, 102, 103] to add them all at once.

Note: requirement_ids must be internal record IDs (returned by create_requirement or get_requirement).
To find IDs for existing requirements, use get_requirement with their tag or number first.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "record_id": {
                        "type": "integer",
                        "description": "Internal record ID of the document. Use for programmatic workflows.",
                    },
                    "tag": {
                        "type": "string",
                        "description": "User-visible document tag, e.g., 'RD-108'.",
                    },
                    "number": {
                        "type": "integer",
                        "description": "User-visible document number without prefix, e.g., 108.",
                    },
                    "requirement_ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "List of requirement record IDs to add to the document.",
                    },
                },
                "required": ["requirement_ids"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    try:
        if name == "list_requirements":
            result = await helix_client.list_requirements(
                fields=arguments.get("fields"),
                search=arguments.get("search"),
                page=arguments.get("page", 1),
                per_page=arguments.get("per_page", 50),
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "get_requirement":
            req_id = await helix_client.resolve_requirement_id(
                record_id=arguments.get("record_id"),
                tag=arguments.get("tag"),
                number=arguments.get("number"),
            )
            result = await helix_client.get_requirement(req_id)
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "create_requirement":
            # Map requirement type names to IDs
            req_type_map = {
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
            req_type = arguments.get("requirement_type", "Functional Requirement")
            req_type_id = req_type_map.get(req_type, 7)

            result = await helix_client.create_requirement(
                summary=arguments["summary"],
                description=arguments.get("description"),
                requirement_type_id=req_type_id,
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "update_requirement":
            req_id = await helix_client.resolve_requirement_id(
                record_id=arguments.get("record_id"),
                tag=arguments.get("tag"),
                number=arguments.get("number"),
            )
            result = await helix_client.update_requirement(
                requirement_id=req_id,
                summary=arguments.get("summary"),
                description=arguments.get("description"),
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "search_requirements":
            result = await helix_client.list_requirements(
                search=arguments["query"],
                fields=arguments.get("fields"),
                page=arguments.get("page", 1),
                per_page=arguments.get("per_page", 50),
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "get_requirement_types":
            result = await helix_client.get_requirement_types()
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "list_requirement_documents":
            result = await helix_client.list_requirement_documents(
                fields=arguments.get("fields"),
                search=arguments.get("search"),
                page=arguments.get("page", 1),
                per_page=arguments.get("per_page", 25),
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "get_document_requirements":
            doc_id = await helix_client.resolve_document_id(
                record_id=arguments.get("record_id"),
                tag=arguments.get("tag"),
                number=arguments.get("number"),
            )
            result = await helix_client.get_document_requirements(
                document_id=doc_id,
                page=arguments.get("page", 1),
                per_page=arguments.get("per_page", 50),
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "create_requirement_document":
            # Map document type names to IDs
            doc_type_map = {
                "PRD": 86,
                "MRD": 87,
                "FMEA": 98,
                "EPIC": 132,
            }
            doc_type = arguments.get("document_type", "PRD")
            doc_type_id = doc_type_map.get(doc_type, 86)

            result = await helix_client.create_requirement_document(
                name=arguments["name"],
                description=arguments.get("description"),
                document_type_id=doc_type_id,
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "add_requirements_to_document":
            doc_id = await helix_client.resolve_document_id(
                record_id=arguments.get("record_id"),
                tag=arguments.get("tag"),
                number=arguments.get("number"),
            )
            result = await helix_client.add_requirements_to_document(
                document_id=doc_id,
                requirement_ids=arguments["requirement_ids"],
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def run_server():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def main():
    """Main entry point."""
    # Load .env file from current directory
    from dotenv import load_dotenv
    load_dotenv()

    # Validate configuration
    if not settings.helix_alm_project:
        print("Error: HELIX_ALM_PROJECT not configured")
        return 1

    if not (settings.has_api_key_auth or settings.has_basic_auth):
        print("Error: No authentication configured")
        return 1

    asyncio.run(run_server())
    return 0


if __name__ == "__main__":
    exit(main())
