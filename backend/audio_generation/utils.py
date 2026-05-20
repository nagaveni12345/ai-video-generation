import re
from django.conf import settings
import os
from groq import Groq

def improve_text_with_groq(text: str) -> str:
    """
    Use Groq LLM to correct grammar and improve clarity of the input text.
    Returns the improved text, or raises an exception if the API call fails.
    """
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    response = client.chat.completions.create(
        model="llama3-8b-8192",  # or "mixtral-8x7b-32768"
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a grammar and clarity editor. "
                    "Fix grammar, punctuation, and phrasing issues in the user's text. "
                    "Return ONLY the corrected text — no explanations, no formatting, no extra commentary."
                ),
            },
            {
                "role": "user",
                "content": text,
            },
        ],
        temperature=0.3,
        max_tokens=1024,
    )

    return response.choices[0].message.content.strip()

def sanitize_text(text):
    """Clean and normalize text for TTS"""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove excessive whitespace
    text = ' '.join(text.split())
    # Remove special characters that might cause issues
    text = re.sub(r'[^\w\s.,!?;:\'\"()-]', '', text)
    return text.strip()

def analyze_text(text):
    """Calculate text metrics"""
    words = text.split()
    # Rough estimate: 2.5 words per second average speaking rate
    estimated_duration = max(1, int(len(words) / 2.5))
    
    return {
        'word_count': len(words),
        'character_count': len(text),
        'estimated_duration_seconds': estimated_duration,
    }

def validate_and_process_text(raw_text):
    """Main validation pipeline"""
    if not raw_text or not isinstance(raw_text, str):
        raise ValueError("Invalid text input")
    
    sanitized = sanitize_text(raw_text)
    
    if len(sanitized) == 0:
        raise ValueError("Text contains no valid characters")
    
    if len(sanitized) > settings.MAX_TEXT_LENGTH:
        raise ValueError(f"Text exceeds maximum length of {settings.MAX_TEXT_LENGTH} characters")
    
    if len(sanitized) < settings.MIN_TEXT_LENGTH:
        raise ValueError(f"Text must be at least {settings.MIN_TEXT_LENGTH} characters")
    
    analysis = analyze_text(sanitized)
    
    return {
        'is_valid': True,
        'sanitized_text': sanitized,
        'analysis': analysis
    }