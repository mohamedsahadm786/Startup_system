import os
import json
from openai import OpenAI

# This reads your API key from the .env file
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def evaluate_startup(
    name: str,
    description: str,
    industry: str,
    stage: str
) -> dict:
    """
    Sends startup details to OpenAI and gets back an evaluation.
    Returns a dictionary with score, strengths, weaknesses, suggestions.
    """

    # This is the prompt we send to OpenAI
    # We tell it exactly what format to respond in (JSON)
    prompt = f"""
You are an expert startup evaluator with 20 years of experience in venture capital.

Evaluate the following startup and respond ONLY with a valid JSON object.
Do not write anything outside the JSON. No explanations, no markdown, just raw JSON.

Startup Details:
- Name: {name}
- Description: {description}
- Industry: {industry}
- Stage: {stage}

Respond with exactly this JSON structure:
{{
    "score": <a number between 0 and 100>,
    "strengths": "<2-3 key strengths as a single string>",
    "weaknesses": "<2-3 key weaknesses as a single string>",
    "suggestions": "<3 specific actionable improvement suggestions as a single string>"
}}
"""

    # Call OpenAI API
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",        # cost effective model for hackathon
        messages=[
            {
                "role": "system",
                "content": "You are a startup evaluator. Always respond with valid JSON only."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,              # 0 = very consistent, 1 = more creative
        max_tokens=500
    )

    # Extract the text response from OpenAI
    raw_text = response.choices[0].message.content.strip()

    # Parse the JSON string into a Python dictionary
    result = json.loads(raw_text)

    # Make sure score is a float
    result["score"] = float(result["score"])

    return result