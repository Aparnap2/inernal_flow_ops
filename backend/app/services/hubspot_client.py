import asyncio
from typing import Dict, Any, List

class HubSpotClient:
    """
    A mock client to simulate interactions with the HubSpot API.
    In a real application, this would make HTTP requests to HubSpot.
    """

    async def get_contact(self, contact_id: str) -> Dict[str, Any]:
        """Simulates fetching a contact from HubSpot."""
        print(f"[HubSpotClient] Fetching contact: {contact_id}")
        await asyncio.sleep(0.1)  # Simulate network latency
        return {
            "id": contact_id,
            "properties": {
                "email": f"contact_{contact_id}@example.com",
                "firstname": "John",
                "lastname": "Doe",
                "jobtitle": "Software Engineer",
            }
        }

    async def get_company(self, company_id: str) -> Dict[str, Any]:
        """Simulates fetching a company from HubSpot."""
        print(f"[HubSpotClient] Fetching company: {company_id}")
        await asyncio.sleep(0.1)
        return {
            "id": company_id,
            "properties": {
                "name": f"Company {company_id} Inc.",
                "domain": f"company{company_id}.com",
                "industry": "Technology",
            }
        }

    async def get_deal(self, deal_id: str) -> Dict[str, Any]:
        """Simulates fetching a deal from HubSpot."""
        print(f"[HubSpotClient] Fetching deal: {deal_id}")
        await asyncio.sleep(0.1)
        return {
            "id": deal_id,
            "properties": {
                "dealname": f"Big Deal {deal_id}",
                "amount": "50000.00",
                "dealstage": "presentationscheduled",
            }
        }

    async def get_associations(
        self, object_type: str, object_id: str
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Simulates fetching associations for a HubSpot object."""
        print(f"[HubSpotClient] Fetching associations for {object_type}:{object_id}")
        await asyncio.sleep(0.1)
        if object_type == "contact":
            return {
                "companies": [{"id": "comp_123", "type": "contact_to_company"}],
                "deals": [{"id": "deal_456", "type": "contact_to_deal"}],
            }
        elif object_type == "company":
            return {
                "contacts": [{"id": "cont_789", "type": "company_to_contact"}],
                "deals": [{"id": "deal_456", "type": "company_to_deal"}],
            }
        return {}
