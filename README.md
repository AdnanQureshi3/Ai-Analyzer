# AI Incident Analyzer

An AI-powered **Retrieval-Augmented Generation (RAG)** system for intelligent incident analysis.  
Automates root cause analysis, pattern detection, and solution generation using **Google Gemini API**, **ChromaDB**, and a FastAPI backend.

This project runs **locally using Docker**, with a Streamlit-based dashboard for visualization.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-green)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

- 🔍 **AI-Powered Analysis**: Root cause analysis and recommendations using Google Gemini  
- 📊 **Smart Pattern Detection**: Detect recurring issues and trends across incidents  
- 🎯 **Auto-Categorization**: AI-driven incident classification and tagging  
- 💡 **Solution Generation**: Context-aware recommendations from historical incidents  
- 📈 **Insight Reports**: Severity trends, frequency analysis, and summaries  
- 🌐 **Web Dashboard**: Streamlit UI for interaction and monitoring  
- 🐳 **Containerized**: Fully Dockerized frontend and backend

---

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python 3.9+  
- **AI / GenAI**: Google Gemini API  
- **Vector Database**: ChromaDB (semantic search & retrieval)  
- **Frontend**: Streamlit  
- **Deployment**: Docker & Docker Compose  

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose  
- Google Gemini API Key  
- Git  

---

### Installation

```bash
# Clone the repository
git clone https://github.com/AdnanQureshi3/Ai-Analyzer.git
cd Ai-Analyzer

# Create vector database directory
mkdir -p chroma_data
chmod -R 777 chroma_data

# Create environment file
touch .env
```

Add your Gemini API key to `.env`:

```env
GEMINI_API_KEY=your_api_key_here
CHROMA_DB_PATH=/app/chroma_data
LOG_LEVEL=INFO
```

Start the application:

```bash
docker-compose up -d --build
docker-compose ps
```

---

## 🌐 Access Services

- **🌐 Web Dashboard**: http://localhost:8501  
- **🔌 API Server**: http://localhost:8000  
- **📚 API Documentation**: http://localhost:8000/docs  

---

## 📖 Usage Examples

### Example 1: Add an Incident

```bash
curl -X POST "http://localhost:8000/api/incidents" \
-H "Content-Type: application/json" \
-d '{
  "incident_id": "INC-2024-001",
  "category": "Database",
  "severity": "High",
  "description": "Database connection pool exhausted during peak traffic"
}'
```

---

### Example 2: Root Cause Analysis

```bash
curl -X POST "http://localhost:8000/api/analyze/root-cause" \
-H "Content-Type: application/json" \
-d '{
  "query": "Database failures during peak hours",
  "k": 5
}'
```

**Example Output:**
```json
{
  "root_cause": "Insufficient connection pool size during peak load",
  "recommendations": [
    "Increase pool size",
    "Add connection pool monitoring",
    "Perform load testing"
  ]
}
```

---

### Example 3: Pattern Analysis

```bash
curl -X POST "http://localhost:8000/api/analyze/patterns" \
-H "Content-Type: application/json" \
-d '{
  "query": "network and authentication issues",
  "k": 8
}'
```

---

### Example 4: Semantic Search

```bash
curl -X GET "http://localhost:8000/api/search?query=database%20timeout&k=5"
```

---

## 🏗️ Project Structure

```
Ai-Analyzer/
├── backend/
│   ├── Dockerfile
│   ├── app/
│   │   └── main.py
│   └── requirements.txt
│
├── frontend/
│   ├── Dockerfile
│   └── app/
│       └── frontend.py
│
├── chroma_data/
├── docker-compose.yml
└── README.md
```

---

## ⚙️ Configuration

### Environment Variables

```env
GEMINI_API_KEY=your_api_key_here
CHROMA_DB_PATH=/app/chroma_data
LOG_LEVEL=INFO
API_BASE_URL=http://backend:8000
```

---

## 🐛 Troubleshooting

### ChromaDB Permission Issues

```bash
chmod -R 777 chroma_data
docker-compose down
docker-compose up -d --build
```

### Port Conflicts

```bash
netstat -tuln | grep -E '(8000|8501)'
```

---

## 📄 License

This project is licensed under the **MIT License**.

---

## ⚠️ Disclaimer

This is a **demo and learning-focused system**.  
AI-generated outputs should always be reviewed before production usage.
