import os
import requests
import yaml
from datetime import datetime

# Load configuration
CONFIG_FILE = "config.yml"
with open(CONFIG_FILE, "r") as file:
    config = yaml.safe_load(file)

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}
SEARCH_QUERY = config["search_query"]
REPOS_PER_PAGE = config["repos_per_page"]
DAILY_LIMIT = config["daily_limit"]
SAVE_DIR = config["save_dir"]

def fetch_repositories(page):
    """Fetch repositories from GitHub."""
    url = f"https://api.github.com/search/code?q={SEARCH_QUERY}&per_page={REPOS_PER_PAGE}&page={page}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("items", [])
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return []

def save_repo(repo, folder):
    """Save repository content."""
    repo_name = repo["repository"]["full_name"].replace("/", "_")
    repo_folder = os.path.join(folder, repo_name)
    if not os.path.exists(repo_folder):
        os.makedirs(repo_folder)
        repo_url = repo["html_url"]
        readme_path = os.path.join(repo_folder, "README.txt")
        with open(readme_path, "w") as file:
            file.write(f"Repository: {repo_url}\n")
        print(f"Saved: {repo_name}")
    else:
        print(f"Skipped (already exists): {repo_name}")

def main():
    """Main function."""
    today = datetime.now().strftime("%Y-%m-%d")
    daily_folder = os.path.join(SAVE_DIR, today)
    os.makedirs(daily_folder, exist_ok=True)

    total_fetched = 0
    for page in range(1, (DAILY_LIMIT // REPOS_PER_PAGE) + 2):
        repos = fetch_repositories(page)
        if not repos:
            break

        for repo in repos:
            if total_fetched >= DAILY_LIMIT:
                break
            save_repo(repo, daily_folder)
            total_fetched += 1

    print(f"Total repositories saved: {total_fetched}")

if __name__ == "__main__":
    main()
