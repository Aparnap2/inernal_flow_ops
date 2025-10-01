#!/usr/bin/env python3
import requests
import json

def test_openrouter_llm():
    print("Testing OpenRouter LLM Integration...")
    
    # OpenRouter API configuration
    api_key = "***REDACTED***"
    base_url = "https://openrouter.ai/api/v1"
    model = "z-ai/glm-4.5-air:free"
    
    url = f"{base_url}/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://your-site.com",
        "X-Title": "HubSpot Operations Orchestrator"
    }
    
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user", 
                "content": "You are a helpful AI assistant. Respond with 'Hello, I am working!' to confirm the connection."
            }
        ],
        "max_tokens": 100,
        "temperature": 0
    }
    
    try:
        print(f"Making request to: {url}")
        print(f"Model: {model}")
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            message = result['choices'][0]['message']['content']
            print(f"LLM Response: {message}")
            return True
        else:
            print(f"Error Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"LLM Error: {e}")
        return False

if __name__ == "__main__":
    success = test_openrouter_llm()
    print(f"LLM Test {'PASSED' if success else 'FAILED'}")
