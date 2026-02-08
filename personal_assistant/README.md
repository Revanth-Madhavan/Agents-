# Personal Assistant Agent (ADK & Outlook)

Your AI-powered executive assistant that organizes your day by analyzing Outlook emails, calendar, and tasks.

## Features

- **Smart Morning Briefing**: Summarizes unread emails and highlights urgent items using LLMs (OpenAI/Google).
- **Meeting Tracker**: Displays today's agenda with context.
- **Task Extraction**: Automatically identifies action items from emails and suggests to-dos.
- **High-End Dashboard**: A clean, modern interface built with Streamlit and custom CSS.

## Setup

1.  **Dependencies**:
    Ensure you run the main setup from the root `PP` folder:

    ```bash
    pip install -r ../requirements.txt
    ```

2.  **Authentication**:
    - This agent shares the same **Microsoft App Registration** credentials as the SharePoint agent (`.env` in root `PP` folder).
    - **Important**: You might need to add `Mail.Read`, `Calendars.Read`, and `Tasks.Read` permissions to your Azure App Registration if they are missing.

3.  **Run the Dashboard**:
    Navigate to this folder and run:
    ```bash
    cd personal_assistant
    streamlit run dashboard.py
    ```

## Structure

- `dashboard.py`: The frontend UI.
- `outlook_service.py`: Backend logic for Microsoft Graph/Outlook.
- `assistant_logic.py`: AI logic for summarization and planning.
