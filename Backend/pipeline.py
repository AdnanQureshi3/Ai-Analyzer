import os
import logging
import re

from dotenv import load_dotenv
from google import genai



GEMINI_MODEL = "gemini-2.5-flash"
TEMPERATURE = 0.2

G_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

class GeminiLLM:
    def invoke(self, prompt: str) -> str:
        if not prompt or not prompt.strip():
            raise ValueError("Empty prompt passed to Gemini")

        response = G_client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[
                {
                    "role": "user",
                    "parts": [{"text": prompt}]
                }
            ],
            config={
                "temperature": TEMPERATURE,
                "max_output_tokens": 2048
            }
        )

        return response.text


class PromptTemplates:
  
    @staticmethod
    def root_cause(context: str, question: str) -> str:
        return f"""
Analyze this incident as an SRE using the provided data. 
Context: {context}
Incident: {question}

Format:
- Primary Root Cause: <one sentence>
- Contributing Factors: <list>
- Evidence: <specific links to history>
- Fix: <immediate action>
- Prevention: <long-term change>

If data is missing, state: "Insufficient historical data to determine root cause."
"""
    @staticmethod
    def pattern(context: str, question: str) -> str:
        return f"""
Identify recurring failure patterns from this data.
Data: {context}
Goal: {question}

Format:
- Recurring Patterns: <list>
- High-Risk Components: <names>
- Severity Trends: <description>
- Recommendations: <list>

If no patterns exist, state that clearly.
"""