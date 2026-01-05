import os
import logging
import re
from typing import List, Dict, Any, Tuple

from dotenv import load_dotenv
from google import genai

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from chromadb import HttpClient

from .embeddings import TransformersEmbedding


DEFAULT_CHROMA_DB_PATH = "/app/chroma_data"
GEMINI_MODEL = "gemini-2.5-flash"
SIMILARITY_THRESHOLD = 0.5
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TEMPERATURE = 0.2

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
You are a senior Site Reliability Engineer and Incident Response Lead.

Your task is to perform a **root cause analysis** using real operational reasoning.
Do NOT give generic answers. If data is insufficient, clearly state assumptions.

HISTORICAL INCIDENT DATA
{context}

CURRENT INCIDENT
{question}

INSTRUCTIONS
- Use only the information given above.
- Correlate patterns across historical incidents.
- Be concrete and technical.
- Do not repeat the incident description.


Primary Root Cause:
- <single most likely cause>

Contributing Factors:
- <factor 1>
- <factor 2>
- <factor 3>

Evidence:
- <specific clues from historical data>

Recommended Immediate Fix:
- <actionable fix>

Long-Term Preventive Measures:
- <systemic improvement>

If analysis is not possible, say:
"Insufficient historical data to determine root cause."
"""

    @staticmethod
    def pattern(context: str, question: str) -> str:
        return f"""
You are a reliability analyst identifying **recurring patterns** across incidents.


HISTORICAL INCIDENT DATA

{context}

FOCUS QUESTION
{question}

OUTPUT FORMAT

Recurring Patterns:
- <pattern 1>
- <pattern 2>

High-Risk Components:
- <component names>

Severity Trends:
- <trend>

Actionable Recommendations:
- <recommendation 1>
- <recommendation 2>

If no meaningful pattern exists, explicitly state that.
"""


class IncidentAnalyzer:
    def __init__(self):
        self.persist_directory = os.getenv("CHROMA_DB_PATH", DEFAULT_CHROMA_DB_PATH)

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

        self.llm = GeminiLLM()

    def _format_docs(self, docs: List[Document]) -> str:
        if not docs:
            return "No similar historical incidents found."
        return "\n\n".join(doc.page_content for doc in docs)

    def ingest_incident(self, incident: Dict[str, Any]) -> bool:
        try:
            content = f"""
INCIDENT ID: {incident.get('incident_id')}
TIMESTAMP: {incident.get('timestamp')}
CATEGORY: {incident.get('category')}
SEVERITY: {incident.get('severity')}
DESCRIPTION: {incident.get('description')}
ROOT CAUSE: {incident.get('root_cause', 'Unknown')}
RESOLUTION: {incident.get('resolution', 'Unknown')}
IMPACT: {incident.get('impact', 'Unknown')}
RESOLUTION TIME MINS: {incident.get('resolution_time_mins')}
"""

            chunks = self.text_splitter.split_text(content)

            docs = [
                Document(
                    page_content=chunk,
                    metadata={
                        "incident_id": incident.get("incident_id"),
                        "severity": incident.get("severity"),
                        "category": incident.get("category"),
                    }
                )
                for chunk in chunks
            ]

            if docs:
                self.vectorstore.add_documents(docs)
                return True

            return False

        except Exception as e:
            logger.error(f"Ingest failed: {e}")
            return False

    def search_incidents(self, query: str, k: int = 5) -> List[Document]:
        try:
            results: List[Tuple[Document, float]] = (
                self.vectorstore.similarity_search_with_score(query, k)
            )

            if not results:
                return []

            filtered = [doc for doc, score in results if score < SIMILARITY_THRESHOLD]
            return filtered if filtered else [doc for doc, _ in results]

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def analyze_root_cause(self, query: str, k: int = 5) -> str:
        logger.info("Analyzing root cause for query: %s", query)

        docs = self.search_incidents(query, k)
        context = self._format_docs(docs)

        prompt = PromptTemplates.root_cause(context, query)

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Prompt length: %d", len(prompt))
            logger.debug("Prompt preview:\n%s", prompt[:1000])

        return self.llm.invoke(prompt)

    def analyze_patterns(self, query: str, k: int = 5) -> str:
        logger.info("Analyzing patterns for query: %s", query)

        docs = self.search_incidents(query, k)
        context = self._format_docs(docs)

        prompt = PromptTemplates.pattern(context, query)

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Prompt length: %d", len(prompt))
            logger.debug("Prompt preview:\n%s", prompt[:1000])

        return self.llm.invoke(prompt)

    def get_stats(self) -> Dict[str, Any]:
        try:
            return {"total_documents": self.vectorstore._collection.count()}
        except Exception:
            return {"total_documents": 0}

    def parse_incident_string(self, doc: str) -> Dict[str, str]:
        incident = {}
        for line in doc.split("\n"):
            m = re.match(r"(?P<k>[A-Z _]+): (?P<v>.+)", line.strip())
            if m:
                incident[m.group("k").lower().replace(" ", "_")] = m.group("v")
        return incident

    def get_incidents(self) -> List[Dict[str, str]]:
        try:
            docs = self.vectorstore.get()["documents"]
            return [self.parse_incident_string(d) for d in docs]
        except Exception:
            return []
