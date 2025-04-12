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
        print(f"Pull Request #{pr['number']}")
        print(f"Title: {pr_data['title']}")
        print(f"Body: {pr_data['body']}")
        print(f"Created At: {pr_data['time']['created_at']}")
        print(f"User: {pr_data['user']['login']} ({pr_data['user']['url']})")
        print("-" * 50)

        # Fetch the files changed in the PR
        files_response = requests.get(pr_data["changes"]["files_url"], headers=headers)

        if files_response.status_code == 200:
            changed_files = files_response.json()
            if not changed_files:
                print("No files changed.")
            else:
                print("Changed Files:")
                for file in changed_files:
                    print(f"File: {file['filename']}")
                    print(f"Status: {file['status']}")
                    print(f"Additions: {file['additions']}")
                    print(f"Deletions: {file['deletions']}")
                    
                    # Print before and after (diff)
                    if 'patch' in file:
                        print("Changes:")
                        print(file['patch'])  # This shows the diff (before and after)
                    else:
                        print("No diff available for this file.")
                    print("-" * 50)
        else:
            print(f"Error: Unable to fetch changed files. Status code: {files_response.status_code}")
        
        print("-" * 50)

def main():
    # Input the repository URL and personal token
    repo_url = "https://github.com/JohnyBoy227/Pull_Analyser" #input("Enter the GitHub repository URL (e.g., https://github.com/owner/repo): ").strip()
    print(f"Received repo URL: {repo_url}")

    # Extract owner and repo from URL
    try:
        owner, repo = repo_url.split("github.com/")[1].split("/")
        print(f"Owner: {owner}, Repo: {repo}")

    except IndexError:
        print("Invalid GitHub repository URL format.")
        return

    token = "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" #input("Enter your GitHub personal access token: ").strip()

    try:
        extract_pull_request_data(owner, repo, token)
    except Exception as e:  # Catch any exception and provide more context
        print(f"An error occurred: {e}")
        if "401" in str(e):  # Example check for an invalid token (HTTP 401 Unauthorized)
            print("Invalid token. Please check your GitHub token and try again.")
    return

if __name__ == "__main__":
    main()