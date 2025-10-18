# utils.py
import os
import openai
import requests
from github import Github

# Set OpenAI API key from environment
openai.api_key = os.getenv("OPENAI_API_KEY")

def verify_secret(secret: str) -> bool:
    """
    Verify that the provided secret matches the expected SECRET_KEY.
    """
    return secret == os.getenv("SECRET_KEY")

def generate_app_from_brief(brief: str, attachments: list) -> dict:
    """
    Generate application files from a brief using OpenAI's Chat Completions API.
    Returns a dictionary of filename -> content.
    """
    messages = [
        {"role": "system", "content": "You are a helpful assistant that generates code files."},
        {"role": "user", "content": f"Generate the code for this brief: {brief}"}
    ]

    # If attachments exist, include them
    if attachments:
        for attachment in attachments:
            messages.append({"role": "user", "content": f"Attachment: {attachment}"})

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    # Expecting the assistant to return JSON mapping filenames -> content
    content = response.choices[0].message.content.strip()

    try:
        files = eval(content)  # assuming assistant returns a dict as a string
        if not isinstance(files, dict):
            raise ValueError("Expected a dictionary from OpenAI response.")
    except Exception:
        # fallback: return a single file 'output.py' with the full content
        files = {"output.py": content}

    return files

def push_files_to_github(files: dict, repo_name: str, branch: str = "main") -> str:
    """
    Push generated files to a GitHub repository.
    Returns the repo URL.
    """
    github_token = os.getenv("GITHUB_TOKEN")
    g = Github(github_token)
    user = g.get_user()
    repo = user.get_repo(repo_name)

    for filename, content in files.items():
        try:
            # Check if file exists
            existing_file = repo.get_contents(filename, ref=branch)
            repo.update_file(filename, f"Update {filename}", content, existing_file.sha, branch=branch)
        except:
            repo.create_file(filename, f"Add {filename}", content, branch=branch)

    return f"https://github.com/{user.login}/{repo_name}"

def post_evaluation(repo_url: str, task: str, round_num: int, email: str, nonce: str):
    """
    Notify the evaluation API about the completed task.
    """
    evaluation_api = os.getenv("EVALUATION_API")
    secret = os.getenv("SECRET_KEY")

    payload = {
        "repo_url": repo_url,
        "task": task,
        "round": round_num,
        "email": email,
        "nonce": nonce,
        "secret": secret
    }

    headers = {"Content-Type": "application/json"}

    try:
        resp = requests.post(evaluation_api, json=payload, headers=headers)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}
