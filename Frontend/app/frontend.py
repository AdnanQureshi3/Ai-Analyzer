import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
import time

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
st.set_page_config(page_title="AI Incident Analyzer", layout="wide", page_icon="🔍")



# will call the backend
def check_api_health():
    max_retries = 3
    retry_delay = 2
    for attempt in range(max_retries):
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                return True
        except:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
    return False


def call_api(endpoint: str, method: str = "GET", data: dict = None, timeout: int = 30):
    url = f"{API_BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=timeout)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=timeout)
        else:
            return None

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error {response.status_code}: {response.text}")
            return None
    except requests.ConnectionError:
        st.error("🚫 Cannot connect to backend.")
    except requests.Timeout:
        st.error("⏰ Backend timeout.")
    except Exception as e:
        st.error(str(e))
    return None


def show_api_status():
    if check_api_health():
        st.sidebar.success("✅ API Connected")
        return True
    st.sidebar.error("❌ API Disconnected")
    return False
