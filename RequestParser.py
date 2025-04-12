import requests
import tkinter as tk
import os
from dotenv import load_dotenv
from portia import (
    Config,
    LLMModel,
    LLMProvider,
    Portia,
    example_tool_registry,
)

# Load .env variables
load_dotenv()
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# Validate key presence
if not ANTHROPIC_API_KEY:
    raise ValueError("Claude API key not found in .env!")

# Set up config using Claude 3.5 Sonnet
anthropic_config = Config.from_default(
    llm_provider=LLMProvider.ANTHROPIC,
    llm_model_name=LLMModel.CLAUDE_3_5_SONNET,
    anthropic_api_key=ANTHROPIC_API_KEY
)

# Initialize Portia
portia = Portia(config=anthropic_config, tools=example_tool_registry)

# Function to run Portia for code review
def review_code(diff: str):
    # Run the code review using Portia and get the result
    review_result = portia.run(f"Review the following code for readability, function length, naming conventions, and possible improvements. Provide a description of what the code does and if the merge should be accepted:\n{diff}")
    
    # Debug: Print the raw review result
    print("Raw Portia output:", review_result)

    # Extract the final output from the review result
    try:
        if hasattr(review_result, "final_output") and review_result.final_output:
            return review_result.final_output
        elif isinstance(review_result, str):
            return review_result  # If the result is already a string
        else:
            return "No final output available from Portia."
    except Exception as e:
        return f"Error extracting final output: {e}"

# Placeholder for extract_pull_request_data
def extract_pull_request_data(owner, repo, token):
    pass  # This will be replaced with the actual implementation later

# Function to check pull requests and review the results
def check_pull_requests(url: str, token: str):
    # Clear the results box
    results_box.config(state=tk.NORMAL)
    results_box.delete(1.0, tk.END)

    # Extract owner and repo from the URL
    try:
        owner, repo = url.split("github.com/")[1].split("/")
        results_box.insert(tk.END, f"Owner: {owner}, Repo: {repo}\n")
    except IndexError:
        results_box.insert(tk.END, "Invalid GitHub repository URL format.\n")
        results_box.config(state=tk.DISABLED)
        return

    # Call the function to extract pull request data with error handling
    try:
        extract_pull_request_data(owner, repo, token)

        # Get the content of the results box
        results_content = results_box.get("1.0", tk.END).strip()
        if results_content:
            # Debug: Print the content being sent to Portia
            print("Content sent to Portia:", results_content)

            # Get the final output from Portia
            review_feedback = review_code(results_content)

            # Debug: Print the final output from Portia
            print("Final Portia output:", review_feedback)

            # Display the final output in the portia_comments_box
            portia_comments_box.config(state=tk.NORMAL)
            portia_comments_box.delete("1.0", tk.END)  # Clear previous feedback
            portia_comments_box.insert(tk.END, review_feedback)  # Insert final output
            portia_comments_box.config(state=tk.DISABLED)
        else:
            portia_comments_box.config(state=tk.NORMAL)
            portia_comments_box.delete("1.0", tk.END)
            portia_comments_box.insert(tk.END, "No content to review.\n")
            portia_comments_box.config(state=tk.DISABLED)

    except Exception as e:
        results_box.insert(tk.END, f"An error occurred while fetching pull request data: {e}\n")

    results_box.config(state=tk.DISABLED)

# Actual implementation of extract_pull_request_data
def extract_pull_request_data(owner, repo, token):
    # Clear the results box
    results_box.config(state=tk.NORMAL)
    results_box.delete(1.0, tk.END)

    # Get all pull requests for the repository
    pulls_url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(pulls_url, headers=headers)

    if response.status_code != 200:
        results_box.insert(tk.END, f"Error: Unable to fetch pull requests. Status code: {response.status_code}\n")
        results_box.config(state=tk.DISABLED)
        return

    pull_requests = response.json()

    if not pull_requests:
        results_box.insert(tk.END, "No open pull requests found.\n")
        results_box.config(state=tk.DISABLED)
        return

    for pr in pull_requests:
        pr_data = {
            "title": pr["title"],
            "body": pr["body"],
            "changes": {
                "additions": pr.get("additions", 0),
                "deletions": pr.get("deletions", 0),
                "commits_url": pr["commits_url"],
                "files_url": pr["url"] + "/files"
            },
            "time": {
                "created_at": pr["created_at"]
            },
            "user": {
                "login": pr["user"]["login"],
                "url": pr["user"]["url"],
                "avatar_url": pr["user"]["avatar_url"]
            }
        }
        # Insert pull request details into the results box
        results_box.insert(tk.END, f"Pull Request #{pr['number']}\n")
        results_box.insert(tk.END, f"Title: {pr_data['title']}\n")
        results_box.insert(tk.END, f"Body: {pr_data['body']}\n")
        results_box.insert(tk.END, f"Created At: {pr_data['time']['created_at']}\n")
        results_box.insert(tk.END, f"User: {pr_data['user']['login']} ({pr_data['user']['url']})\n")
        results_box.insert(tk.END, "-" * 50 + "\n")

        # Fetch the files changed in the PR
        files_response = requests.get(pr_data["changes"]["files_url"], headers=headers)

        if files_response.status_code == 200:
            changed_files = files_response.json()
            if not changed_files:
                results_box.insert(tk.END, "No files changed.\n")
            else:
                results_box.insert(tk.END, "Changed Files:\n")
                for file in changed_files:
                    results_box.insert(tk.END, f"File: {file['filename']}\n")
                    results_box.insert(tk.END, f"Status: {file['status']}\n")
                    results_box.insert(tk.END, f"Additions: {file['additions']}\n")
                    results_box.insert(tk.END, f"Deletions: {file['deletions']}\n")
                    if 'patch' in file:
                        results_box.insert(tk.END, "Changes:\n")
                        results_box.insert(tk.END, file['patch'] + "\n")
                    else:
                        results_box.insert(tk.END, "No diff available for this file.\n")
                    results_box.insert(tk.END, "-" * 50 + "\n")
        else:
            results_box.insert(tk.END, f"Error: Unable to fetch changed files. Status code: {files_response.status_code}\n")
        results_box.insert(tk.END, "-" * 50 + "\n")

    # Disable the results box after updating
    results_box.config(state=tk.DISABLED)

# Tkinter GUI Setup
window = tk.Tk()
window.geometry("700x700")

# Create a label
window.title("GitHub Pull Request Checker")
window.configure(bg="#f0f0f0")

# GitHub URL Label and Entry
url_label = tk.Label(window, text="GitHub URL (e.g., https://github.com/owner/repo):")
url_label.pack(pady=5)
url_entry = tk.Entry(window, width=70)
url_entry.pack(pady=5)

# GitHub API Token Label and Entry
token_label = tk.Label(window, text="GitHub API Token:")
token_label.pack(pady=5)
token_entry = tk.Entry(window, width=70, show="*")  # 'show="*"' hides the input for security
token_entry.pack(pady=5)

# Button to Check for Pull Requests
check_button = tk.Button(window, text="Check for Pull Requests", command=lambda: check_pull_requests(url_entry.get(), token_entry.get()))
check_button.pack(pady=10)

# Multi-line text box to display the results
results_box = tk.Text(window, height=10, width=70)
results_box.pack(pady=10)
results_box.config(state=tk.DISABLED)

# Multi-line text box to load the Portia comments into it:
portia_comments_box = tk.Text(window, height=5, width=70)
portia_comments_box.pack(pady=20)
portia_comments_box.config(state=tk.DISABLED)
portia_comments_box.insert(tk.END, "Portia comments box")

# Run the Tkinter event loop
window.mainloop()
