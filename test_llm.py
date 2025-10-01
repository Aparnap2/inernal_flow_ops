#!/usr/bin/env python3
import asyncio
import sys
import os
sys.path.append('/home/aparna/Desktop/flow_ops/backend')

from app.services.llm_client import get_llm_client
from app.config import settings

async def test_llm():
    print("Testing LLM Integration...")
    print(f"OpenAI Base URL: {settings.OPENAI_BASE_URL}")
    print(f"Model: {settings.OPENAI_MODEL}")
    
    try:
        llm = get_llm_client()
        
        # Test simple completion
        response = await llm.ainvoke("You are a helpful AI assistant. Respond with 'Hello, I am working!' to confirm the connection.")
        print(f"LLM Response: {response.content}")
        return True
    except Exception as e:
        print(f"LLM Error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_llm())
