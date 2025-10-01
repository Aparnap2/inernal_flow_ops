#!/usr/bin/env python3
"""Test script to verify OpenRouter LLM client works"""

import asyncio
from app.services.llm_client import get_llm_client
from langchain_core.messages import HumanMessage

async def test_openrouter_client():
    """Test OpenRouter client with a simple query"""
    try:
        print("🧪 Testing OpenRouter LLM client...")
        
        llm = get_llm_client()
        print(f"✅ LLM client created with model: {llm.model_name}")
        
        # Simple test query
        response = await llm.ainvoke([
            HumanMessage(content="Say 'Hello from OpenRouter!' in exactly 5 words.")
        ])
        
        print(f"✅ Response received: {response.content}")
        return True
        
    except Exception as e:
        print(f"❌ OpenRouter test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_openrouter_client())
    if success:
        print("\n✅ OpenRouter integration working!")
    else:
        print("\n❌ OpenRouter integration failed!")
