import requests

def extract_pull_request_data(owner, repo, token):
    # Get all pull requests for the repository
    pulls_url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(pulls_url, headers=headers)

    if response.status_code != 200:
        print(f"Error: Unable to fetch pull requests. Status code: {response.status_code}")
        return

    pull_requests = response.json()

    if not pull_requests:
        print("No open pull requests found.")
        return

    for pr in pull_requests:
        pr_data = {
            "title": pr["title"],
            "body": pr["body"],
            "changes": {
                "additions": pr_data.get("additions", 0),
                "deletions": pr_data.get("deletions", 0),
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
        print(f"Pull Request #{pr['number']}")
        print(f"Title: {pr_data['title']}")
        print(f"Body: {pr_data['body']}")
        print(f"Created At: {pr_data['time']['created_at']}")
        print(f"User: {pr_data['user']['login']} ({pr_data['user']['url']})")
        print(f"Changes: Commits - {pr_data['changes']['commits_url']}, Files - {pr_data['changes']['files_url']}")
        print("-" * 50)

def main():
    # Input the repository URL and personal token
    repo_url = input("Enter the GitHub repository URL (e.g., https://github.com/owner/repo): ").strip()
    print(f"Received repo URL: {repo_url}")
    token = input("Enter your GitHub personal access token: ").strip()

    # Extract owner and repo from URL
    try:
        owner, repo = repo_url.split("github.com/")[1].split("/")
    except IndexError:
        print("Invalid GitHub repository URL format.")
        return

    extract_pull_request_data(owner, repo, token)

if __name__ == "__main__":
    main()