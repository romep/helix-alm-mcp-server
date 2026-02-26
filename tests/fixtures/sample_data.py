"""Sample data from Helix ALM for testing.

This data was exported from the Sample Project and represents
known-good values for comparison in tests.

Source: tests/HelixALMTextExport - 01_27_2026 9_38_06 pm.txt
        API exploration during development
"""

# Documents - known values from export
# Note: Tag format for documents is "RD-{number}" based on API pattern
DOCUMENTS = {
    "test_1": {
        "number": 108,
        "tag": "RD-108",
        "name": "Test 1",
        "requirement_count": 3,
    },
    "test_2": {
        "number": 109,
        "tag": "RD-109",
        "name": "Test 2",
        "requirement_count": 0,
    },
    "headphone_5": {
        "number": 91,
        "tag": "RD-91",
        "name": "Project: Headphone 5",
        "requirement_count": 27,
    },
    "headphone_6": {
        "number": 94,
        "tag": "RD-94",
        "name": "Project: Headphone 6",
        "requirement_count": 15,
    },
    "fmea": {
        "number": 98,
        "tag": "RD-98",
        "name": "Headphone IV FMEA",
        "requirement_count": 4,
    },
    "mrd": {
        "number": 100,
        "tag": "RD-100",
        "name": "MRD New Headphone Product",
        "requirement_count": 10,
    },
}

# Requirements - known values from API exploration
# These are actual requirements from the Sample Project
REQUIREMENTS = {
    "business_need": {
        "record_id": 1969,
        "number": 1960,
        "tag": "BR-1960",
        "summary": "Business Need: Online Customer Order Tracking System",
        "type": "Business Requirement",
    },
    "user_accounts": {
        "record_id": 1970,
        "number": 1961,
        "tag": "FR-1961",
        "summary": "User Accounts",
        "type": "Functional Requirement",
    },
    "order_lookup": {
        "record_id": 1971,
        "number": 1962,
        "tag": "FR-1962",
        "summary": "Order Look-up",
        "type": "Functional Requirement",
    },
}

# Tag prefixes by requirement type (for reference)
TAG_PREFIXES = {
    "Business Requirement": "BR",
    "Functional Requirement": "FR",
    "User Story": "US",
    "Non-Functional Requirement": "NFR",
    "Technical Requirement": "TR",
    "Security Requirement": "SR",
    "Performance Requirement": "PR",
    "Design Note": "DN",
    "Risk": "RK",
    "Use Case": "UC",
    "Overview": "OV",
    "Task": "TK",
    "Glossary": "GL",
    "Hazards": "HZ",
    "Harms": "HM",
}
