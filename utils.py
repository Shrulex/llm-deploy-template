# utils.py
import os
import openai
from github import Github
import requests

# Load environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
SECRET_KEY = os.getenv("SECRET_KEY")
EVALUATION_API = os.getenv("EVALUATION_API")

openai.api_key = OPENAI_API_KEY


# ------------- Step 1: Verify Secret ----------------
def verify_secret(secret):
    return secret == SECRET_KEY


# ------------- Step 2: Generate App from Brief -------------
def generate_app_from_brief(brief, attachments):
    """
    Generates code (HTML/JS/etc.) from the task brief using OpenAI's new API
    Returns a dict of filenames -> file contents
    """
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that writes complete web apps."},
            {"role": "user", "content": brief}
        ],
        temperature=0
    )

    code = response.choices[0].message.content

    # For simplicity, we will save everything in index.html for now
    files = {"index.html": code}

    # If attachments exist, you could decode and add them here
    for attachment in attachments:
        name = attachment["name"]
        url = attachment["url"]
        if url.startswith("data:"):
            import base64
            data = url.split(",")[1]
            files[name] = base64.b64decode(data).decode("utf-8")

    return files


# ------------- Step 3: Push Files to GitHub -------------
def push_files_to_github(repo_name, files, commit_message):
    """
    Creates repo (or uses existing), pushes files, returns (repo_url, commit_sha)
    """
    g = Github(GITHUB_TOKEN)

    # Check if repo exists, otherwise create
    user = g.get_user()
    try:
        repo = user.get_repo(repo_name)
    except:
        repo = user.create_repo(repo_name, private=False)

    # Push files
    commit_sha = None
    for filename, content in files.items():
        try:
            file = repo.get_contents(filename)
            repo.update_file(filename, commit_message, content, file.sha)
        except:
            file = repo.create_file(filename, commit_message, content)
        commit_sha = file.sha

    repo_url = repo.html_url
    return repo_url, commit_sha


# ------------- Step 4: POST to Evaluation API -------------
def post_evaluation(payload):
    """
    Sends the payload to instructor's evaluation API
    """
    headers = {"Content-Type": "application/json"}
    try:
        resp = requests.post(EVALUATION_API, json=payload, headers=headers)
        resp.raise_for_status()
    except Exception as e:
        print(f"Error posting evaluation: {e}")
