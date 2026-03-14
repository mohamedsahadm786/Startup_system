import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def analyze_pitch_deck(extracted_text: str, startup_name: str) -> dict:
    """
    Sends extracted pitch deck text to OpenAI.
    Returns score, analysis, key insights, and improvement suggestions.
    """

    # Limit text to 3000 characters to stay within token limits
    # Pitch decks can be very long — we take the most important part
    text_to_analyze = extracted_text[:3000]

    prompt = f"""
You are an expert pitch deck analyst and venture capital advisor.

Analyze the following pitch deck content for a startup called "{startup_name}".
Respond ONLY with a valid JSON object. No markdown, no explanation, just raw JSON.

Pitch Deck Content:
{text_to_analyze}

Respond with exactly this JSON structure:
{{
    "score": <a number between 0 and 100 reflecting overall pitch quality>,
    "analysis": "<overall analysis of the pitch deck in 3-4 sentences>",
    "key_insights": "<3 key insights or strengths found in the pitch deck>",
    "improvements": "<3 specific improvements to make the pitch deck stronger>"
}}
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a pitch deck analyst. Always respond with valid JSON only."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
        max_tokens=600
    )

    raw_text = response.choices[0].message.content.strip()

    result = json.loads(raw_text)
    result["score"] = float(result["score"])

    return result