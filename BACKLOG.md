# Helix ALM MCP Server - Backlog & Known Limitations

This document tracks intentional limitations in the current release and candidates for future enhancement. These items are out of scope for the initial proof-of-concept but represent natural next steps.

---

## Known Limitations

### 1. Document Tree Structure - Flat Only

**Current Behavior:** All requirements added via `add_requirements_to_document` are placed at the top level of the document tree.

**Limitation:** Cannot create hierarchical document structures (nested requirements, sections) through the MCP server.

**Workaround:** Use the Helix ALM desktop client or web UI to reorganize requirements into a hierarchy after adding them.

**Future Enhancement:**

```python
add_requirements_to_document(
    document_id: int,
    requirement_ids: list[int],
    parent_node_id: int | None = None  # If None, adds to top level; otherwise adds as children of specified node
)
```

Additional tools for full hierarchy support:
```python
get_document_tree(document_id: int) -> dict  # Returns full tree structure with node IDs
add_child_requirements(document_id: int, parent_node_id: int, requirement_ids: list[int])
move_requirement_in_document(document_id: int, node_id: int, new_parent_node_id: int | None)
```

---

### 2. No Delete Operations

**Current Behavior:** The MCP server does not implement any delete operations for requirements, requirement documents, or other items.

**Rationale:** Delete operations are destructive and irreversible. For a proof-of-concept integration, we intentionally omit these to prevent accidental data loss. This is especially important when AI assistants are involved, as they may misinterpret intent.

**Workaround:** Use the Helix ALM desktop client or web UI to delete items.

**Future Enhancement:** If delete support is added, it should include:
- Confirmation mechanisms
- Soft-delete where available
- Clear warnings in tool descriptions
- Possibly a "dry-run" mode

---

### 3. No Issue or Test Case Support

**Current Behavior:** Only requirements and requirement documents are supported.

**Limitation:** Helix ALM's Issues and Test Cases modules are not accessible through this MCP server.

**Workaround:** Use the Helix ALM clients directly for issue tracking and test management.

**Future Enhancement:** Phase 2 and 3 from the original roadmap:
- Issues: `list_issues`, `get_issue`, `create_issue`, `update_issue`, `search_issues`
- Test Cases: `list_test_cases`, `get_test_case`, `list_test_runs`, `create_test_run`

---

### 4. No Attachment Support

**Current Behavior:** Cannot upload, download, or manage file attachments on requirements or documents.

**Workaround:** Manage attachments through the Helix ALM UI.

**Future Enhancement:**
```python
upload_attachment(item_type: str, item_id: int, file_path: str)
list_attachments(item_type: str, item_id: int)
download_attachment(item_type: str, item_id: int, attachment_id: int)
```

---

### 5. No Workflow Event Support

**Current Behavior:** Cannot trigger workflow transitions or add workflow events to items.

**Limitation:** Items remain in their initial workflow state after creation.

**Workaround:** Use Helix ALM UI to transition items through workflow states.

**Future Enhancement:**
```python
add_workflow_event(item_type: str, item_id: int, event_type: str, comment: str | None)
get_workflow_events(item_type: str, item_id: int)
```

---

### 6. No Link Management

**Current Behavior:** Cannot create, view, or manage links between items (requirement-to-requirement, requirement-to-test-case, etc.).

**Workaround:** Create traceability links through the Helix ALM UI.

**Future Enhancement:**
```python
create_link(source_type: str, source_id: int, target_type: str, target_id: int, link_type: str)
get_links(item_type: str, item_id: int)
```

---

### 7. Limited Field Support

**Current Behavior:** Create and update operations support a subset of fields (Summary, Description, Tag, Type). Custom fields are not directly supported.

**Workaround:** Edit custom fields through the Helix ALM UI after creation.

**Future Enhancement:** Dynamic field discovery and support:
```python
get_field_definitions(item_type: str)  # Returns all available fields with IDs and types
create_requirement(..., custom_fields: dict[str, Any])  # Support arbitrary fields
```

---

### 8. SSL Certificate Verification Disabled

**Current Behavior:** SSL verification is disabled (`verify=False`) to accommodate self-signed certificates common in Helix ALM deployments.

**Security Note:** This is acceptable for proof-of-concept and internal deployments but should be configurable for production use.

**Future Enhancement:**
```bash
# Environment variable to control SSL verification
HELIX_ALM_VERIFY_SSL=true
HELIX_ALM_CA_BUNDLE=/path/to/ca-bundle.crt
```

---

### 9. No Bulk Create Operations

**Current Behavior:** Requirements must be created one at a time via `create_requirement`.

**Limitation:** Creating many requirements (e.g., importing from a PRD) requires multiple sequential API calls.

**Note:** The Helix ALM REST API does support batch creation; this is a limitation of the current MCP server implementation.

**Future Enhancement:**
```python
create_requirements(
    requirements: list[dict]  # Each dict contains summary, description, requirement_type, etc.
) -> list[dict]  # Returns list of created requirements with IDs
```

---

### 10. No Folder Support

**Current Behavior:** Cannot organize requirements into folders or retrieve folder structure.

**Limitation:** Helix ALM supports organizing items into folder hierarchies. This MCP server does not expose folder operations.

**Workaround:** Organize requirements into folders through the Helix ALM UI.

**Future Enhancement:**
```python
list_folders(item_type: str) -> dict  # Returns folder tree structure
get_folder_contents(folder_id: int, item_type: str) -> list[dict]
add_to_folder(item_type: str, item_id: int, folder_id: int)
remove_from_folder(item_type: str, item_id: int, folder_id: int)
```

---

### 11. No Report Execution

**Current Behavior:** Cannot execute saved reports from Helix ALM.

**Limitation:** Helix ALM allows users to create and save reports. This MCP server cannot run those reports or retrieve their results.

**Workaround:** Run reports through the Helix ALM desktop client or web UI.

**Future Enhancement:**
```python
list_reports(item_type: str | None = None) -> list[dict]  # List available saved reports
run_report(report_id: int) -> dict  # Execute report and return results
```

---

## Ideas & Suggestions

*Space for capturing ideas that come up during development or user feedback.*

- [ ] Bulk operations for efficiency (create multiple requirements in one call)
- [ ] Template support (create requirements from predefined templates)
- [ ] Export capabilities (export document to markdown/PDF)
- [ ] Caching for frequently accessed data (requirement types, field definitions)
- [ ] Rate limit handling with automatic retry
- [ ] Webhook support for real-time updates

---

## Contributing

If you'd like to contribute to any of these enhancements, please open an issue on GitHub to discuss the approach before submitting a pull request.

---

*Last Updated: January 21, 2026*
