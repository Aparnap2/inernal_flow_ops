import asyncio
from typing import Dict, Any

class NotionClient:
    """
    A mock client to simulate interactions with the Notion API.
    """

    async def attach_sop_link(self, page_id: str, sop_url: str) -> Dict[str, Any]:
        """Simulates attaching a link to a Notion page."""
        print(f"[NotionClient] Attaching SOP link {sop_url} to page {page_id}")
        await asyncio.sleep(0.1) # Simulate network latency
        return {"status": "ok", "page_id": page_id}
