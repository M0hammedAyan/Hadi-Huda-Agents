import logging
import os
import re
import requests
import smtplib
from typing import Optional
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from livekit.agents import function_tool, RunContext
from langchain_community.tools import DuckDuckGoSearchRun
from car_diagnostics import CarDiagnostics

# Initialize car diagnostics engine once
diagnostic_engine = CarDiagnostics()


# 🧠 CAR DIAGNOSTIC TOOL
@function_tool()
async def diagnose_car_issue(
    context: RunContext,  # type: ignore
    query: str
) -> str:
    """
    Diagnose car issues locally using the car_problems.json knowledge base.
    Example:
        - 'My engine is overheating'
        - 'The car won’t start'
        - 'Brakes are not working'
    """
    try:
        logging.info(f"Diagnosing car issue for query: {query}")
        result = diagnostic_engine.get_response(query)
        logging.info(f"Diagnosis result: {result[:150]}...")  # Trim log output
        return result
    except Exception as e:
        logging.error(f"Error diagnosing issue: {e}")
        return f"An error occurred during diagnosis: {e}"


# 🌦️ WEATHER TOOL
@function_tool()
async def get_weather(
    context: RunContext,  # type: ignore
    city: str
) -> str:
    """
    Get the current weather for a given city using wttr.in
    Example: "What's the weather in London?"
    """
    try:
        response = requests.get(f"https://wttr.in/{city}?format=3")
        if response.status_code == 200:
            weather = response.text.strip()
            logging.info(f"Weather for {city}: {weather}")
            return weather
        else:
            logging.error(f"Weather API failed: {response.status_code}")
            return f"Could not retrieve weather for {city}."
    except Exception as e:
        logging.error(f"Error retrieving weather: {e}")
        return f"An error occurred while retrieving weather for {city}."


# 🌐 WEB SEARCH TOOL
@function_tool()
async def search_web(
    context: RunContext,  # type: ignore
    query: str
) -> str:
    """
    Perform a quick web search using DuckDuckGo.
    Example: "Search for the history of Tesla Motors"
    """
    try:
        results = DuckDuckGoSearchRun().run(tool_input=query)
        logging.info(f"Search results for '{query}': {results[:150]}...")
        return results
    except Exception as e:
        logging.error(f"Error searching web: {e}")
        return f"An error occurred while searching for '{query}'."


# 📧 EMAIL SENDING TOOL
@function_tool()
async def send_email(
    context: RunContext,  # type: ignore
    to_email: str,
    subject: str,
    message: str,
    cc_email: Optional[str] = None
) -> str:
    """
    Send an email via Gmail SMTP.
    Requires environment variables:
        GMAIL_USER, GMAIL_APP_PASSWORD
    """
    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        gmail_user = os.getenv("GMAIL_USER")
        gmail_password = os.getenv("GMAIL_APP_PASSWORD")

        if not gmail_user or not gmail_password:
            return "Email sending failed: Gmail credentials not configured."

        msg = MIMEMultipart()
        msg["From"] = gmail_user
        msg["To"] = to_email
        msg["Subject"] = subject
        recipients = [to_email]

        if cc_email:
            msg["Cc"] = cc_email
            recipients.append(cc_email)

        msg.attach(MIMEText(message, "plain"))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(gmail_user, gmail_password)
            server.sendmail(gmail_user, recipients, msg.as_string())

        logging.info(f"✅ Email sent successfully to {to_email}")
        return f"Email sent successfully to {to_email}"

    except smtplib.SMTPAuthenticationError:
        logging.error("Gmail authentication failed")
        return "Authentication error. Please check your Gmail credentials."
    except smtplib.SMTPException as e:
        logging.error(f"SMTP error: {e}")
        return f"SMTP error occurred: {str(e)}"
    except Exception as e:
        logging.error(f"Unexpected error while sending email: {e}")
        return f"An error occurred: {str(e)}"
