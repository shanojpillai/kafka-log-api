import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import json
import time
from datetime import datetime
import os

# Set page config
st.set_page_config(
    page_title="Kafka Log Monitoring Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Define API URL
API_URL = os.environ.get("API_URL", "http://localhost:8000")

# Add title and description
st.title("Kafka Log Monitoring Dashboard")
st.markdown("""
This dashboard visualizes log data flowing through the Kafka system.
Monitor real-time log events, analyze patterns, and filter logs by various criteria.
""")

# Define functions to interact with the API
def get_logs(level=None, service=None, limit=100):
    """Fetch logs from the API with optional filters."""
    params = {"limit": limit}
    if level:
        params["level"] = level
    if service:
        params["service"] = service
        
    try:
        response = requests.get(f"{API_URL}/api/v1/logs", params=params)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching logs: {response.status_code} - {response.text}")
            return {"status": "error", "logs": []}
    except Exception as e:
        st.error(f"Error connecting to API: {e}")
        return {"status": "error", "logs": []}

def get_dataset_info():
    """Fetch dataset information from the API."""
    try:
        response = requests.get(f"{API_URL}/api/v1/dataset/info")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching dataset info: {response.status_code} - {response.text}")
            return {"status": "error"}
    except Exception as e:
        st.error(f"Error connecting to API: {e}")
        return {"status": "error"}

def send_log(service, level, message, metadata=None):
    """Send a log entry to the API."""
    payload = {
        "service": service,
        "level": level,
        "message": message
    }
    if metadata:
        payload["metadata"] = metadata
        
    try:
        response = requests.post(f"{API_URL}/api/v1/log", json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error sending log: {response.status_code} - {response.text}")
            return {"status": "error"}
    except Exception as e:
        st.error(f"Error connecting to API: {e}")
        return {"status": "error"}

def send_sample_log(index):
    """Send a sample log from the dataset."""
    try:
        response = requests.get(f"{API_URL}/api/v1/kaggle/{index}")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error sending sample log: {response.status_code} - {response.text}")
            return {"status": "error"}
    except Exception as e:
        st.error(f"Error connecting to API: {e}")
        return {"status": "error"}

# Sidebar for controls
st.sidebar.header("Controls")

# Refresh rate
refresh_rate = st.sidebar.slider("Refresh Rate (seconds)", 5, 60, 10)

# Filters
st.sidebar.subheader("Log Filters")
level_filter = st.sidebar.selectbox("Log Level", ["All", "INFO", "WARN", "ERROR"])
service_filter = st.sidebar.text_input("Service Name", "")
log_limit = st.sidebar.number_input("Number of Logs", 10, 1000, 100)

# Log sender
st.sidebar.subheader("Send Log")
with st.sidebar.form("send_log_form"):
    service_input = st.text_input("Service", "test-service")
    level_input = st.selectbox("Level", ["INFO", "WARN", "ERROR"])
    message_input = st.text_area("Message", "This is a test log message")
    metadata_input = st.text_area("Metadata (JSON, optional)", '{"source": "streamlit-dashboard"}')
    
    submit_button = st.form_submit_button("Send Log")
    if submit_button:
        try:
            metadata = json.loads(metadata_input) if metadata_input else None
            result = send_log(service_input, level_input, message_input, metadata)
            if result["status"] == "success":
                st.sidebar.success("Log sent successfully!")
            else:
                st.sidebar.error("Failed to send log.")
        except json.JSONDecodeError:
            st.sidebar.error("Invalid JSON in metadata field.")

# Sample log sender
st.sidebar.subheader("Send Sample Log")
sample_index = st.sidebar.number_input("Sample Log Index", 0, 10000, 0)
if st.sidebar.button("Send Sample Log"):
    result = send_sample_log(sample_index)
    if result["status"] == "success":
        st.sidebar.success(f"Sample log {sample_index} sent successfully!")
    else:
        st.sidebar.error("Failed to send sample log.")

# Dataset info
st.sidebar.subheader("Dataset Info")
if st.sidebar.button("Refresh Dataset Info"):
    dataset_info = get_dataset_info()
    if dataset_info["status"] == "success":
        st.sidebar.success(f"Dataset contains {dataset_info.get('total_logs', 'unknown')} logs")
    else:
        st.sidebar.error("Failed to fetch dataset info.")

# Main dashboard content
col1, col2 = st.columns(2)

with col1:
    st.subheader("Log Level Distribution")
    log_data = get_logs(limit=log_limit)
    
    if log_data["status"] == "success" and log_data["logs"]:
        df_logs = pd.DataFrame(log_data["logs"])
        
        # Count logs by level
        level_counts = df_logs["level"].value_counts().reset_index()
        level_counts.columns = ["Level", "Count"]
        
        # Create pie chart
        fig = px.pie(level_counts, values="Count", names="Level", 
                    title="Log Distribution by Level",
                    color="Level", 
                    color_discrete_map={"INFO": "green", "WARN": "orange", "ERROR": "red"})
        st.plotly_chart(fig)
    else:
        st.info("No logs available to display.")

with col2:
    st.subheader("Log Timeline")
    if log_data["status"] == "success" and log_data["logs"]:
        df_logs = pd.DataFrame(log_data["logs"])
        
        # Ensure timestamp is parsed properly
        if "_kafka_timestamp" in df_logs.columns:
            df_logs["timestamp"] = pd.to_datetime(df_logs["_kafka_timestamp"], unit="ms")
        else:
            # Try multiple formats if exact format is unknown
            try:
                df_logs["timestamp"] = pd.to_datetime(df_logs["timestamp"])
            except:
                df_logs["timestamp"] = datetime.now()
        
        # Group by time and level
        df_logs["hour"] = df_logs["timestamp"].dt.floor("H")
        timeline_data = df_logs.groupby(["hour", "level"]).size().reset_index(name="count")
        
        # Create line chart
        fig = px.line(timeline_data, x="hour", y="count", color="level",
                    title="Log Frequency Over Time",
                    color_discrete_map={"INFO": "green", "WARN": "orange", "ERROR": "red"})
        fig.update_layout(xaxis_title="Time", yaxis_title="Number of Logs")
        st.plotly_chart(fig)
    else:
        st.info("No logs available to display timeline.")

# Recent logs table
st.subheader("Recent Logs")

# Apply filters
filtered_level = None if level_filter == "All" else level_filter
filtered_service = service_filter if service_filter else None

log_data = get_logs(level=filtered_level, service=filtered_service, limit=log_limit)

if log_data["status"] == "success" and log_data["logs"]:
    df_logs = pd.DataFrame(log_data["logs"])
    
    # Select columns to display
    display_columns = ["timestamp", "level", "service", "message"]
    for col in display_columns:
        if col not in df_logs.columns:
            df_logs[col] = ""
    
    # Format the dataframe for display
    df_display = df_logs[display_columns].copy()
    
    # Style the dataframe
    def highlight_level(val):
        if val == "ERROR":
            return "background-color: #ffcccc"
        elif val == "WARN":
            return "background-color: #ffffcc"
        elif val == "INFO":
            return "background-color: #ccffcc"
        return ""
    
    # Display the table
    st.dataframe(df_display.style.applymap(highlight_level, subset=["level"]))
else:
    st.info("No logs available to display with the current filters.")

# Auto-refresh
if st.checkbox("Enable auto-refresh", value=True):
    st.empty()
    st.info(f"Dashboard will refresh every {refresh_rate} seconds.")
    time.sleep(refresh_rate)
    st.experimental_rerun()