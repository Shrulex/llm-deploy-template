import os
import requests
from github import Github

def verify_secret(secret):
    return secret == os.environ.get("SECRET_KEY")

def push_to_github(repo_name, folder_path, commit_msg="Update app"):
    g = Github(os.environ["GITHUB_TOKEN"])
    user = g.get_user()
    
    try:
        repo = user.get_repo(repo_name)
    except:
        repo = user.create_repo(repo_name, private=False, license_template="mit")

    # Commit all files from folder_path
    for root, dirs, files in os.walk(folder_path):
        for f in files:
            file_path = os.path.join(root, f)
            rel_path = os.path.relpath(file_path, folder_path)
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
            try:
                contents = repo.get_contents(rel_path)
                repo.update_file(contents.path, commit_msg, content, contents.sha)
            except:
                repo.create_file(rel_path, commit_msg, content)
    return repo.html_url, repo.get_commits()[0].sha

def post_evaluation(payload):
    url = os.environ["EVALUATION_API"]
    headers = {"Content-Type": "application/json"}
    requests.post(url, json=payload, timeout=10)
