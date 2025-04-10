import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = "python-poetry/poetry"
API_URL = f"https://api.github.com/repos/{REPO}/issues"

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def fetch_issue_timeline(issue_number):
    """Fetches the timeline events for a given issue number and extracts relevant details."""
    url = f"https://api.github.com/repos/python-poetry/poetry/issues/{issue_number}/timeline"
    headers = {"Accept": "application/vnd.github.v3+json"}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching timeline for issue {issue_number}: {response.status_code}")
        return []

    events = response.json()
    return format_issue_timeline(events)

def format_issue_timeline(events):
    """Formats the timeline events to only include event_type, author, event_date, label, and comment."""
    formatted_events = []
    
    for event in events:
        formatted_event = {
            "event_type": event.get("event"),
            "author": event.get("actor", {}).get("login", "") if event.get("actor") else "",
            "event_date": event.get("created_at"),
            "label": event.get("label", {}).get("name") if event.get("event") == "labeled" else "",
            "comment": event.get("body") if event.get("event") == "commented" else ""
        }
        formatted_events.append(formatted_event)

    return formatted_events
def format_issue(issue):
    """Format issue data into a clean structure."""
    return {
        "url": issue.get("html_url"),
        "creator": issue.get("user", {}).get("login"),
        "labels": [label["name"] for label in issue.get("labels", [])],
        "state": issue.get("state"),
        "assignees": [assignee["login"] for assignee in issue.get("assignees", [])],
        "title": issue.get("title"),
        "text": issue.get("body", "").replace("\r", "") if issue.get("body") else "",
        "number": issue.get("number"),
        "created_date": issue.get("created_at"),
        "updated_date": issue.get("updated_at"),
        "timeline_url": f"https://api.github.com/repos/python-poetry/poetry/issues/{issue.get('number')}/timeline",
        "events": fetch_issue_timeline(issue.get("number"))
    }

all_issues = []
page = 1

while True:
    response = requests.get(API_URL, headers=headers, params={"state": "all", "per_page": 100, "page": page})
    
    if response.status_code != 200:
        print(f"Error {response.status_code}: {response.text}")
        break

    issues = response.json()
    if not issues:
        break  # Stop if no more issues

    formatted_issues = [format_issue(issue) for issue in issues]
    all_issues.extend(formatted_issues)
    page += 1  # Fetch next page

# Save as JSON file
with open("poetry_data.json", "w", encoding="utf-8") as f:
    json.dump(all_issues, f, indent=4)

print(f"Saved {len(all_issues)} formatted issues to poetry_data.json")
