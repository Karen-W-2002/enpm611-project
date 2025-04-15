import requests
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = "python-poetry/poetry"
API_URL = f"https://api.github.com/repos/{REPO}/issues"

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def check_rate_limit():
    """Check GitHub API rate limit and sleep if necessary."""
    resp = requests.get("https://api.github.com/rate_limit", headers=HEADERS)
    data = resp.json()
    remaining = data["rate"]["remaining"]
    reset_time = data["rate"]["reset"]
    
    if remaining == 0:
        sleep_time = reset_time - int(time.time()) + 5
        print(f"Rate limit hit. Sleeping for {sleep_time} seconds...")
        time.sleep(sleep_time)

def fetch_issue_timeline(issue_number):
    """Fetch timeline for a given issue."""
    url = f"https://api.github.com/repos/{REPO}/issues/{issue_number}/timeline"
    check_rate_limit()
    
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Error fetching timeline for issue {issue_number}: {response.status_code}")
        return []

    return format_issue_timeline(response.json())

def format_issue_timeline(events):
    """Formats the timeline events."""
    formatted_events = []
    for event in events:
        formatted_events.append({
            "event_type": event.get("event"),
            "author": event.get("actor", {}).get("login", "") if event.get("actor") else "",
            "event_date": event.get("created_at"),
            "label": event.get("label", {}).get("name") if event.get("event") == "labeled" else "",
            "comment": event.get("body") if event.get("event") == "commented" else ""
        })
    return formatted_events

def format_issue(issue):
    """Format basic issue data + timeline."""
    timeline = fetch_issue_timeline(issue.get("number"))
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
        "closed_date": issue.get("closed_at"),
        "timeline_url": f"https://api.github.com/repos/{REPO}/issues/{issue.get('number')}/timeline",
        "events": timeline
    }

all_issues = []
page = 1

while True:
    check_rate_limit()
    print(f"Fetching page {page}...")

    response = requests.get(API_URL, headers=HEADERS, params={"state": "all", "per_page": 50, "page": page})
    
    if response.status_code != 200:
        print(f"Error {response.status_code}: {response.text}")
        break

    issues = response.json()
    if not issues:
        break

    for issue in issues:
        # Optional: Skip PRs, as they also appear in /issues endpoint
        if "pull_request" in issue:
            continue
        all_issues.append(format_issue(issue))
        time.sleep(1)  # Small delay between issue fetches

    page += 1

with open("poetry_data.json", "w", encoding="utf-8") as f:
    json.dump(all_issues, f, indent=4)

print(f"Saved {len(all_issues)} issues to poetry_data.json")