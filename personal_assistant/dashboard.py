import streamlit as st
import os
import datetime
from outlook_service import OutlookManager
from assistant_logic import PersonalAssistant
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Personal Assistant", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for "High Landing Page" feel
st.markdown("""
<style>
    .stApp {
        background-color: #f0f2f6; 
    }
    .metric-card {
        padding: 20px;
        border-radius: 10px;
        background-color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 20px;
    }
    .email-card {
        padding: 15px;
        border-radius: 8px;
        background-color: white;
        margin-bottom: 10px;
        border-left: 5px solid #0078d4; /* Outlook Blue */
    }
    .action-badge {
        background-color: #ffd700;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: bold;
        font-size: 0.8em;
    }
    h1, h2, h3 {
        color: #333;
    }
</style>
""", unsafe_allow_html=True)

st.title("Good Morning, User ☀️")
st.subheader("Here is your Personalized Briefing")

# Initialize Helpers
if "manager" not in st.session_state:
    client_id = os.getenv("SHAREPOINT_CLIENT_ID")
    client_secret = os.getenv("SHAREPOINT_CLIENT_SECRET")
    tenant_id = os.getenv("SHAREPOINT_TENANT_ID")
    st.session_state.manager = OutlookManager(client_id, client_secret, tenant_id)
    
if "assistant" not in st.session_state:
    st.session_state.assistant = PersonalAssistant()

# Authentication Check
try:
    if not st.session_state.manager.account.is_authenticated:
        st.warning("Please authenticate with Microsoft Outlook")
        # Logic to trigger auth flow (usually CLI or OAuth link logic)
        st.session_state.manager.authenticate()
        st.experimental_rerun()
except Exception as e:
    st.error(f"Authentication Setup Issue: {e}")

# Main Data Fetch (Turbocharged via cache/session state)
if "daily_data" not in st.session_state:
    with st.spinner("Fetching emails and syncing calendar..."):
        # 1. Fetch Emails
        emails_raw = st.session_state.manager.get_unread_emails_summary(limit=5)
        # 2. Analyze via AI
        email_summary = st.session_state.assistant.analyze_emails(emails_raw)
        
        # 3. Fetch Calendar
        meetings = st.session_state.manager.get_todays_meetings()
        
        st.session_state.daily_data = {
            "emails": email_summary,
            "meetings": meetings,
            "tasks": ["Review Project Plan", "Send Weekly Report"] # Mock tasks for now as API logic is tricky
        }

data = st.session_state.daily_data

# Dashboard Layout
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="metric-card"><h3>📧 Inbox</h3><p>5 Unread</p><p>2 Urgent</p></div>', unsafe_allow_html=True)

with col2:
    st.markdown(f'<div class="metric-card"><h3>📅 Meetings</h3><p>{len(data["meetings"])} Today</p><p>Next: 10:00 AM</p></div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card"><h3>✅ Tasks</h3><p>3 High Priority</p><p>8 Backlog</p></div>', unsafe_allow_html=True)


# Main Content Area
tab1, tab2, tab3 = st.tabs(["Daily Briefing", "Calendar", "Task Board"])

with tab1:
    st.header("Executive Summary")
    st.write(st.session_state.assistant.plan_day(data["meetings"], data["tasks"]))
    
    st.markdown("### 📨 Priority Correspondence")
    for mail in data["emails"]:
        priority_color = "red" if mail.get("priority") == "High" else "gray"
        st.markdown(f"""
        <div class="email-card" style="border-left-color: {priority_color};">
            <b>{mail['sender']}</b> | {mail['original_subject']}<br>
            <span style="color: #666; font-size: 0.9em;">{mail['summary']}</span><br>
            <div style="margin-top: 5px;">
                <span class="action-badge">Action: {mail['action_item']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns([1, 4])
        if cols[0].button("Add to Tasks", key=f"add_{mail['original_subject']}"):
            st.toast(f"Added '{mail['action_item']}' to To-Do List")

with tab2:
    st.header("Today's Agenda")
    if not data["meetings"]:
        st.info("No meetings scheduled for today! 🎉")
    else:
        for m in data["meetings"]:
            st.markdown(f"**{m['subject']}** ({m['start']} - {m['end']}) @ {m['location']}")
            if m['body_preview']:
                st.caption(m['body_preview'])
            st.divider()

with tab3:
    st.header("Task Management")
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Today")
        for t in data["tasks"]:
            st.checkbox(t)
            
    with c2:
        st.subheader("Backlog / Upcoming")
        st.write("- Q1 Planning")
        st.write("- Vendor Assessment")
        st.text_input("Add new backlog item...")

