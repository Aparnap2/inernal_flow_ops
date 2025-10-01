#!/usr/bin/env python3
"""Test script to check imports and basic functionality"""

import sys
import traceback

def test_imports():
    """Test all critical imports"""
    try:
        print("Testing FastAPI import...")
        from fastapi import FastAPI
        print("✅ FastAPI imported successfully")
        
        print("Testing LangGraph imports...")
        from langgraph.checkpoint.redis import RedisSaver
        print("✅ LangGraph Redis checkpoint imported successfully")
        
        print("Testing Redis import...")
        import redis.asyncio as redis
        print("✅ Redis async imported successfully")
        
        print("Testing app config...")
        from app.config import settings
        print("✅ App config imported successfully")
        
        print("Testing app services...")
        from app.services.redis_service import redis_service
        print("✅ Redis service imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        traceback.print_exc()
        return False

def test_basic_fastapi():
    """Test basic FastAPI functionality"""
    try:
        from fastapi import FastAPI
        app = FastAPI()
        
        @app.get("/test")
        def test_endpoint():
            return {"status": "ok"}
            
        print("✅ Basic FastAPI app created successfully")
        return True
        
    except Exception as e:
        print(f"❌ FastAPI test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Running import and basic functionality tests...\n")
    
    success = True
    success &= test_imports()
    success &= test_basic_fastapi()
    
    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
