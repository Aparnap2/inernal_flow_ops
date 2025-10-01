import asyncio
from typing import Dict, Any

class AirtableClient:
    """
    A mock client to simulate interactions with the Airtable API.
    """

    async def upsert_record(self, base_id: str, table_name: str, record: Dict[str, Any]) -> Dict[str, Any]:
        """Simulates upserting a record to an Airtable base."""
        print(f"[AirtableClient] Upserting record to {base_id}/{table_name}: {record.get('id')}")
        await asyncio.sleep(0.1) # Simulate network latency
        return {
            "id": record.get("id", "rec_new_id"),
            "fields": record,
            "createdTime": "2025-09-29T00:00:00.000Z",
        }
