import re

# max allowed query lenght - to prevent token stuffing attacks
MAX_QUERY_LENGTH = 500

# prompt-injection attack signatures
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions",
    r"disregard\s+(all\s+)?(previous|prior|rules)",
    r"system\s+prompt\s+(verbatim|verbatum|leak|reveal)",
    r"you\s+are\s+now\s+(in\s+)?(dan|developer\s+mode|unrestricted)",
    r"print\s+your\s+(api\s+key|credentials|secret)",
]

# Regex patterns to detect leaked API keys
SECRET_PATTERNS = [
    # Grok API Keys
    r"gsk_[a-zA-Z0-9]{20,}",
    # Tavily API Keys
    r"tvly-[a-zA-Z0-9]{20,}",
    # Langsmith API Keys
    r"lsv2_[a-zA-Z0-9_]{20,}",
    # WeatherAPI API Keys
    r"[a-f0-9]{32}",
]


def detect_toxic_content(text: str) -> tuple[bool, str]:
    """
    Toxicity Guardrail: Simple profanity filter for public-facing AI.
    Returns (contains_toxicity, reason)
    """
    toxicity_keywords = ["fuck", "shit", "bitch", "damn"]
    text_lower = text.lower()
    for keyword in toxicity_keywords:
        if keyword in text_lower:
            return True, "Your response was flagged for containing inappropriate language."
    return False, ""


def validate_input(user_query: str) -> tuple[bool, str]:
    """
    Input Guardrail: Validates length and detects prompt injection attempts.
    Returns (is_safe, error_message).
    """
    # Length check
    if len(user_query.strip()) > MAX_QUERY_LENGTH:
        return False, f"Query too long. Please limit your question to {MAX_QUERY_LENGTH} characters."

    # Prompt injection pattern check
    query_lower = user_query.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, query_lower):
            return False, "Security Notice: Your query was flagged for attempting to override system guidelines."
            
    # Toxicity Check (NEW)
    is_toxic, reason = detect_toxic_content(user_query)
    if is_toxic:
        return False, reason
    return True, ""


def sanitize_location(location: str) -> str:
    """
    Tool Guardrail: 
    Cleans and validates location strings before calling WeatherAPI.
    """
    # Strip HTML tags, script brackets, and control characters
    cleaned = re.sub(r"[<>/{}\[\]\\]", "", location).strip()
    # cap location string to 100 chars
    return cleaned[:100]


def sanitize_output(text: str) -> str:
    """
    Output Guardrail: 
    Scans final text and redacts any accidental API key leaks.
    """
    # Redact API Keys
    cleaned_text = text
    for pattern in SECRET_PATTERNS:
        cleaned_text = re.sub(pattern, "[REDACTED_API_KEY]", cleaned_text)

    # Toxic content check in final response
    is_toxic, _ = detect_toxic_content(cleaned_text)
    if is_toxic:
        return "I apologize, but the response was flagged for inappropriate content and cannot be displayed."
    return cleaned_text

