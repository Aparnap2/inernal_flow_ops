from langchain_openai import ChatOpenAI
from app.config import settings

def get_llm_client(temperature: float = 0) -> ChatOpenAI:
    """
    Get configured LLM client for OpenRouter/OpenAI compatibility
    """
    return ChatOpenAI(
        model=settings.OPENAI_MODEL,
        temperature=temperature,
        openai_api_key=settings.OPENAI_API_KEY,
        openai_api_base=settings.OPENAI_BASE_URL,
        default_headers={
            "HTTP-Referer": settings.SITE_URL,
            "X-Title": settings.SITE_NAME,
        }
    )
