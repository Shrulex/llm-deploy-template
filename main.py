from flask import Flask, request, jsonify
import os, uuid
from utils import verify_secret, generate_app_from_brief, push_files_to_github, post_evaluation

app = Flask(__name__)

@app.route("/api-endpoint", methods=["POST"])
def api_endpoint():
    data = request.json
    if not verify_secret(data.get("secret")):
        return jsonify({"error": "Invalid secret"}), 403

    task = data.get("task")
    round_num = data.get("round", 1)
    email = data.get("email")
    nonce = data.get("nonce")
    brief = data.get("brief")
    attachments = data.get("attachments", [])

    # --- Step A: Generate app using LLM ---
    files = generate_app_from_brief(brief, attachments)

    # --- Step B: Push to GitHub ---
    repo_name = f"{task}"
    repo_url, commit_sha = push_files_to_github(repo_name, files, f"Round {round_num} update")

    # --- Step C: Send evaluation POST ---
    pages_url = f"https://{os.environ['GITHUB_TOKEN'].split('_')[1]}.github.io/{repo_name}/"
    payload = {
        "email": email,
        "task": task,
        "round": round_num,
        "nonce": nonce,
        "repo_url": repo_url,
        "commit_sha": commit_sha,
        "pages_url": pages_url
    }
    post_evaluation(payload)

    return jsonify({"status": "success", "repo_url": repo_url, "commit_sha": commit_sha}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
