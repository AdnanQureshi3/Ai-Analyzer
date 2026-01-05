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



#data fetching
def fetch_incidents():
    try:
        res = requests.get(f"{API_BASE_URL}/api/incidents", timeout=10)
        if res.status_code == 200:
            return res.json().get("results", [])
    except:
        pass
    return []


def create_sample_data():
    return [
        {
            "incident_id": f"INC-{i:05d}",
            "timestamp": (datetime.now() - timedelta(days=i)).isoformat(),
            "category": ["Database","Network","Application","Security","Infrastructure"][i % 5],
            "severity": ["Low","Medium","High","Critical"][i % 4],
            "description": f"Sample incident {i}",
            "resolution_time_mins": [1,2,4,8,12,24][i % 6],
        }
        for i in range(50)
    ]



# Visualization Functions
def create_metrics_row(incidents):
    """Create metrics overview row"""
    if not incidents:
        incidents = create_sample_data()
    
    df = pd.DataFrame(incidents)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Incidents", len(incidents))
    
    with col2:
        if not df.empty and 'severity' in df.columns:
            critical = len(df[df['severity'] == 'Critical'])
            st.metric("Critical Incidents", critical, delta=f"{critical/len(df)*100:.1f}%")
    
    with col3:
        if not df.empty and 'resolution_time_mins' in df.columns:
            mttr = df['resolution_time_mins'].mean()
            st.metric("Mean MTTR", f"{mttr:.1f}m")
    
    with col4:
        if not df.empty and 'category' in df.columns:
            unique_categories = df['category'].nunique()
            st.metric("Categories", unique_categories)

def create_category_distribution(incidents):
    """Create category distribution chart"""
    if not incidents:
        incidents = create_sample_data()
    
    df = pd.DataFrame(incidents)
    
    if df.empty or 'category' not in df.columns:
        return
    
    category_counts = df['category'].value_counts().reset_index()
    category_counts.columns = ['Category', 'Count']
    
    fig = px.pie(category_counts, values='Count', names='Category', 
                 title='Incidents by Category', hole=0.4)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(showlegend=False)
    
    st.plotly_chart(fig, use_container_width=True)

def create_severity_timeline(incidents):
    """Create severity timeline chart"""
    if not incidents:
        incidents = create_sample_data()
    
    df = pd.DataFrame(incidents)
    
    if df.empty or 'timestamp' not in df.columns or 'severity' not in df.columns:
        return
    
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['date'] = df['timestamp'].dt.date
    daily_counts = df.groupby(['date', 'severity']).size().reset_index(name='count')
    
    fig = px.line(daily_counts, x='date', y='count', color='severity',
                  title='Daily Incidents by Severity',
                  labels={'date': 'Date', 'count': 'Number of Incidents', 'severity': 'Severity'})
    
    st.plotly_chart(fig, use_container_width=True)
