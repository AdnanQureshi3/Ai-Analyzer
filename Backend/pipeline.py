import os
import logging
import re

from dotenv import load_dotenv
from google import genai
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from .embeddings import TransformersEmbedding
from chromadb import HttpClient
from langchain_chroma import Chroma


GEMINI_MODEL = "gemini-2.5-flash"
TEMPERATURE = 0.2
SIMILARITY_THRESHOLD = 0.5
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
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
    
class IncidentAnalyzer:
    def __init__(self):
        self.llm = GeminiLLM()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )
        self.embeddings = TransformersEmbedding("thenlper/gte-small")
        self.vectorstore = Chroma(
            collection_name="incidents",
            client=HttpClient(host="localhost", port=8000),
            embedding_function=self.embeddings
        )

    def get_incidents(self) -> List[Dict[str, str]]:
        try:
            docs = self.vectorstore.get()["documents"]
            return [self.parse_incident_string(d) for d in docs]
        except Exception:
            return []
