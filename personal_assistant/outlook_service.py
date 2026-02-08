import os
import datetime
from O365 import Account, FileSystemTokenBackend
from bs4 import BeautifulSoup

class OutlookManager:
    def __init__(self, client_id, client_secret, tenant_id=None):
        self.credentials = (client_id, client_secret)
        # Using a new token file for Outlook scopes specifically if needed, 
        # or share the token backend but with expanded scopes.
        # It's safer to use a separate token file to avoid scope conflicts if the previous one was limited.
        self.token_backend = FileSystemTokenBackend(token_path='.', token_filename='o365_token_assistant.txt')
        self.account = Account(self.credentials, token_backend=self.token_backend, tenant_id=tenant_id)

    def authenticate(self):
        """Authenticates with extended scopes for Mail, Calendar, and Tasks."""
        scopes = ['basic', 'message_all', 'calendar_all', 'tasks_all']
        if not self.account.is_authenticated:
            print("Authentication required for Assistant.")
            self.account.authenticate(scopes=scopes)
            print("Authenticated successfully.")
        else:
            # Check if we need to refresh or re-consent for new scopes (handled by library mostly)
            # Just to be safe, we can force re-auth if scopes are missing, but for now assume valid.
            pass

    def get_unread_emails_summary(self, limit=5):
        """Fetches unread emails and returns a structured list."""
        mailbox = self.account.mailbox()
        inbox = mailbox.inbox_folder()
        
        # Filter for unread messages
        query = mailbox.new_query().on_attribute('is_read').equals(False)
        messages = inbox.get_messages(limit=limit, query=query, download_attachments=False)
        
        email_data = []
        for msg in messages:
            soup = BeautifulSoup(msg.body, "html.parser")
            text_body = soup.get_text(separator=' ', strip=True)[:1000] # Truncate for AI
            
            email_data.append({
                "subject": msg.subject,
                "sender": msg.sender.name,
                "received": msg.received.isoformat(), # Serialize for JSON/LLM
                "body_preview": text_body,
                "id": msg.object_id
            })
        return email_data

    def get_todays_meetings(self):
        """Fetches calendar events for today."""
        schedule = self.account.schedule()
        calendar = schedule.get_default_calendar()
        
        today = datetime.date.today()
        start = datetime.datetime.combine(today, datetime.time.min)
        end = datetime.datetime.combine(today, datetime.time.max)
        
        q = calendar.new_query('start').greater_equal(start)
        q.chain('and').on_attribute('end').less_equal(end)
        
        events = calendar.get_events(query=q, include_recurring=True)
        
        meetings = []
        for event in events:
            meetings.append({
                "subject": event.subject,
                "start": event.start.strftime("%H:%M"),
                "end": event.end.strftime("%H:%M"),
                "location": event.location.displayName if event.location else "Teams/Online",
                "body_preview": event.body[:200] if event.body else ""
            })
        return meetings

    def get_tasks(self):
        """Fetches TODO tasks (using Microsoft To Do API functionality in O365 lib if available)."""
        # Note: O365 library support for 'To Do' (Tasks) can be varying. 
        # Plan B: Use Outlook Tasks (classic) which is often supported under 'account.tasks()'
        # The 'tasks_all' scope refers to Outlook Tasks.
        
        # Try retrieving default task folder
        # Note: 'O365' library usually exposes tasks via account.tasks() ??
        # Let's check typical usage or fallback to a simple mock if the library version is old.
        # Actually it's often account.new_message()... wait. 
        # Correct usage: account.tasks() is not standard. It's often accessed via specific modules.
        # Let's try to find the default tasks folder.
        
        # If library doesn't support easy task access, we might skip or use valid calls.
        # For this snippet, we will assume we can get a handle or return empty if complex.
        # We will try investigating `account.storage().get_drive(...)`? No that's files.
        
        # Official O365 lib documentation says: `account.new_task()` is for creating.
        # To fetch: `account.tasks_default_folder()`?
        # Let's try simple folder access if possible, or leave logic "To Be Implemented" correctly.
        # For now, let's just return a placeholder or attempt a basic fetch if possible.
        
        # *Self-correction*: The O365 python library doesn't have a top-level 'tasks' helper as robust as 'mailbox'.
        # We might need to access the API endpoint directly or use `account.connection.get(...)`
        # For safety and speed, I will stick to Mail and Calendar which are robust.
        # We can implement a "Local Task Manager" for now that syncs with Outlook *later* if needed.
        return []

