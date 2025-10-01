import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from app.workflows.company_intake import CompanyIntakeState, start_intake, normalize_company_data


@pytest.mark.asyncio
async def test_start_intake():
    """Test the start_intake node function."""
    initial_state = {
        "hubspot_event": {},
        "enriched_data": {},
        "normalized_data": {},
        "airtable_record": {},
        "notion_page_id": "",
        "kickoff_scheduled": False
    }
    
    result = await start_intake(initial_state)
    
    # Verify the result
    assert result["kickoff_scheduled"] == False
    assert "kickoff_scheduled" in result


@pytest.mark.asyncio
async def test_normalize_company_data():
    """Test the normalize_company_data node function."""
    test_state = {
        "hubspot_event": {},
        "enriched_data": {
            "details": {
                "id": "test_id",
                "properties": {
                    "name": "Test Company",
                    "domain": "test.com",
                    "industry": "Technology",
                    "lifecyclestage": "customer"
                }
            }
        },
        "company_data": {
            "name": "Test Company",
            "domain": "test.com",
            "industry": "Technology",
            "lifecyclestage": "customer"
        },
        "normalized_data": {},
        "airtable_record": {},
        "notion_page_id": "",
        "kickoff_scheduled": False,
        "requires_approval": False,
        "approval_data": {},
        "final_result": {},
        "errors": []
    }
    
    result = await normalize_company_data(test_state)
    
    # Verify the normalization worked
    assert result["normalized_data"]["Name"] == "Test Company"
    assert result["normalized_data"]["Domain"] == "test.com"
    assert result["normalized_data"]["Industry"] == "Technology"
    assert result["normalized_data"]["Lifecycle Stage"] == "customer"


if __name__ == "__main__":
    asyncio.run(test_start_intake())
    asyncio.run(test_normalize_company_data())
    print("All tests passed!")