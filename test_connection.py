#!/usr/bin/env python3
"""Quick test script to verify Helix ALM API connection."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dotenv import load_dotenv
load_dotenv()

from helix_alm_mcp.client import helix_client, format_requirement_summary, extract_field_value
from helix_alm_mcp.config import settings


async def test_connection():
    """Test the connection to Helix ALM."""
    print(f"Testing connection to: {settings.helix_alm_api_url}")
    print(f"Project: {settings.helix_alm_project}")
    print(f"Auth method: {'API Key' if settings.has_api_key_auth else 'Basic Auth'}")
    print("-" * 60)

    try:
        # Test authentication
        print("\n1. Authenticating...")
        token = await helix_client.authenticate()
        print(f"   SUCCESS - Token: {token[:30]}...")

        # Test listing requirements
        print("\n2. Listing requirements...")
        result = await helix_client.list_requirements(per_page=5)

        if "requirements" in result:
            reqs = result["requirements"]
            print(f"   SUCCESS - Found {len(reqs)} requirements")
            for req in reqs[:5]:
                summary = format_requirement_summary(req)
                print(f"   - [{summary['tag']}] {summary['summary'][:50] if summary['summary'] else 'No summary'}...")

        # Test getting requirement types
        print("\n3. Getting requirement types...")
        types = await helix_client.get_requirement_types()
        if "requirementTypesData" in types:
            print(f"   SUCCESS - Found {len(types['requirementTypesData'])} types:")
            for rt in types["requirementTypesData"][:5]:
                print(f"   - {rt.get('label', rt)}")

        # Test listing requirement documents
        print("\n4. Listing requirement documents...")
        docs = await helix_client.list_requirement_documents()
        if "documents" in docs:
            doc_list = docs["documents"]
            print(f"   SUCCESS - Found {len(doc_list)} documents")
            for doc in doc_list[:5]:
                name = extract_field_value(doc, "Name") or "Unnamed"
                print(f"   - [{doc.get('tag')}] {name}")

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED!")
        print("\nYour MCP server is ready. To use it:")
        print("  1. Add to Claude Desktop config (see README)")
        print("  2. Or run directly: helix-alm-mcp")

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await helix_client.close()


if __name__ == "__main__":
    asyncio.run(test_connection())
