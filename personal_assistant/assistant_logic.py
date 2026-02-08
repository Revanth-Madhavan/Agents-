import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv

load_dotenv()

class PersonalAssistant:
    def __init__(self):
        # Default to GPT unless configured otherwise
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

    def analyze_emails(self, emails: list):
        """
        Summarizes emails and extracts actionable items.
        
        Args:
            emails (list): List of email dicts {sender, subject, body_preview}
            
        Returns:
            list: List of analyzed items {summary, priority, action_item, context}
        """
        if not emails:
            return []

        # Prompt for batch processing (or loop individually if too long)
        # For simplicity, let's process top 5 together or loop.
        
        results = []
        
        template = """
        You are my personal executive assistant. Analyze this email.
        
        Sender: {sender}
        Subject: {subject}
        Content: {body_preview}
        
        Task:
        1. Summarize the core message in 1 sentence.
        2. Assign a priority (High, Medium, Low) based on urgency/sender.
        3. Identify any requested action item or meeting.
        4. Suggest a direct next step for me.
        
        Output JSON format only:
        {{
            "summary": "...",
            "priority": "...",
            "action_item": "...",
            "next_step": "..."
        }}
        """
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | self.llm | JsonOutputParser()

        for email in emails:
            try:
                analysis = chain.invoke(email)
                analysis['original_subject'] = email['subject']
                analysis['sender'] = email['sender']
                results.append(analysis)
            except Exception as e:
                # Fallback if parsing fails
                results.append({
                    "summary": "Could not analyze automatically.",
                    "priority": "Unknown",
                    "action_item": "Review manually",
                    "next_step": "Open email",
                    "original_subject": email['subject'],
                    "sender": email['sender']
                })
        
        return results

    def plan_day(self, meetings: list, tasks: list):
        """
        Generates a daily briefing/schedule narrative.
        """
        # Simple structured text for now
        context = f"Meetings Today: {len(meetings)}\nTasks Pending: {len(tasks)}"
        return f"Good morning! You have {len(meetings)} meetings scheduling today. Focus on clearing your inbox first."
