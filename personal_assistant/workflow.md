# Personal Assistant Workflow Diagram

This document illustrates the execution flow of the Personal Assistant Agent.

```mermaid
graph TD
    User([User]) -->|Opens Dashboard| Streamlit_App[Streamlit Dashboard]
    Streamlit_App -->|Check Authentication| Outlook_Service[Outlook Service (O365)]

    Outlook_Service -->|Authenticated?| Auth_Check{Is Authenticated?}
    Auth_Check -->|No| Auth_Flow[Initiate O365 Auth Flow]
    Auth_Flow --> Outlook_Service
    Auth_Check -->|Yes| Fetch_Data[Data Fetching]

    subgraph Data_Collection ["Data Collection (Parallel)"]
        direction TB
        Fetch_Emails[Fetch Unread Emails]
        Fetch_Calendar[Fetch Today's Calendar]
        Fetch_Tasks[Fetch Tasks/ToDo]
    end

    Fetch_Data --> Fetch_Emails
    Fetch_Data --> Fetch_Calendar

    subgraph AI_Processing ["AI Analysis (LLM)"]
        Fetch_Emails -->|Email Data| AI_Logic[Assistant Logic (LangChain)]
        AI_Logic -->|Summarize & Prioritize| LLM_Engine[LLM (OpenAI/Gemini)]
        LLM_Engine -->|JSON Insights| AI_Logic
    end

    AI_Logic --> Aggregation[Aggregate Daily Briefing]
    Fetch_Calendar --> Aggregation
    Fetch_Tasks --> Aggregation

    Aggregation -->|Render UI| Streamlit_App

    Streamlit_App -->|View Dashboard| Display_Content

    subgraph User_Interface ["Frontend Dashboard"]
        Display_Content -->|Tab 1| Briefing[Morning Briefing & Inbox Summary]
        Display_Content -->|Tab 2| Schedule[Meeting Agenda]
        Display_Content -->|Tab 3| Tasks[Task Board]
    end

    Briefing -->|Details| Card_View[Priority Email Cards]
    Card_View -->|Add to Task| Action_Button[Action Item Button]
    Action_Button -->|Update State| Streamlit_App

```

## Workflow Explanation

1.  **Start**: The user launches the Streamlit application.
2.  **Authentication**: The system checks for a valid OAuth token (`o365_token_assistant.txt`). If missing, it prompts for Microsoft login.
3.  **Data Ingestion**: The `OutlookManager` fetches unread emails and calendar events via the Microsoft Graph API using the `O365` Python library.
4.  **Intelligence Layer**:
    - Raw email content is passed to the `PersonalAssistant` class.
    - The LLM (OpenAI/Gemini) analyzes each email to generate a concise summary, priority level, and an actionable next step.
5.  **Presentation**: The aggregated data is displayed on a modern dashboard, organized into tabs for easy consumption.
6.  **Interaction**: Users can add tasks directly from email insights or view their schedule.
