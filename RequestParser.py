import json

# Sample JSON object (as a string)
pr_data_json = """
{
  "title": "Add new feature",
  "body": "This pull request adds a new feature to the project.",
  "created_at": "2023-03-01T12:34:56Z",
  "user": {
    "login": "contributor"
  },
  "additions": 100,
  "deletions": 10,
  "changed_files": 5
}
"""

# Parse JSON into a Python dictionary
pr_data = json.loads(pr_data_json)

# Extract required details
title = pr_data.get("title")
body = pr_data.get("body")
created_at = pr_data.get("created_at")
user = pr_data.get("user", {}).get("login")
changes = {
    "additions": pr_data.get("additions", 0),
    "deletions": pr_data.get("deletions", 0),
    "changed_files": pr_data.get("changed_files", 0)
}

# Output the extracted details
print(f"Title: {title}")
print(f"Body: {body}")
print(f"Created At: {created_at}")
print(f"User: {user}")
print(f"Changes: {changes}")