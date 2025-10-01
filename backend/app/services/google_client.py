import asyncio
from typing import Dict, Any

class GoogleClient:
    """
    A mock client to simulate interactions with Google Calendar API.
    """

    async def create_calendar_event(self, event_details: Dict[str, Any]) -> Dict[str, Any]:
        """Simulates creating a Google Calendar event."""
        print(f"[GoogleClient] Creating calendar event: {event_details.get('summary')}")
        await asyncio.sleep(0.1) # Simulate network latency
        return {
            "id": "evt_random_id",
            "summary": event_details.get("summary"),
            "status": "confirmed",
            "htmlLink": "https://calendar.google.com/event?id=evt_random_id",
        }
