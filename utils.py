import os
import openai
from github import Github
import requests

openai.api_key = os.environ.get("OPENAI_API_KEY")

# -----------------------------
# Step 2: LLM App Generator
# -----------------------------
def generate_app_from_brief(brief, attachments=[]):
    """
    Generates minimal HTML/CSS/JS app using LLM.
    attachments: list of {"name": ..., "url": ...} (data URI)
    """
    attachment_text = ""
    for a in attachments:
        attachment_text += f"\nAttachment: {a['name']} (encoded content included)\n"

    prompt = f"""
You are an expert web developer.
Create a minimal HTML/CSS/JS app that fulfills the following brief:
{brief}
Include attachments as embedded data if needed.
Output a ZIP-style structure as JSON like:
{{
  "files": [
    {{"path": "index.html", "content": "..."}},
    {{"path": "README.md", "content": "..."}}
  ]
}}
Do not include explanations outside JSON.
"""
    resp = openai.ChatCompletion.create(
        model="gpt-4-32k",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    text = resp.choices[0].message.content

    import json
    try:
        data = json.loads(text)
        return data.get("files", [])
    except:
        return [{"path": "index.html", "content": f"<html><body><h1>{brief}</h1></body></html>"}]

# -----------------------------
# Step 3: Push to GitHub
# -----------------------------
def push_files_to_github(repo_name, files, commit_msg="Update app"):
    g = Github(os.environ["GITHUB_TOKEN"])
    user = g.get_user()
    
    try:
        repo = user.get_repo(repo_name)
    except:
        repo = user.create_repo(repo_name, private=False, license_template="mit")

    for file in files:
        path = file["path"]
        content = file["content"]
        try:
            existing = repo.get_contents(path)
            repo.update_file(existing.path, commit_msg, content, existing.sha)
        except:
            repo.create_file(path, commit_msg, content)
    
    return repo.html_url, repo.get_commits()[0].sha

# -----------------------------
# Optional: Verify secret
# -----------------------------
def verify_secret(secret):
    return secret == os.environ.get("SECRET_KEY")

# -----------------------------
# Optional: POST to evaluation API
# -----------------------------
def post_evaluation(payload):
    url = os.environ.get("EVALUATION_API")
    headers = {"Content-Type": "application/json"}
    requests.post(url, json=payload, timeout=10)
