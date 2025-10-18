from flask import Flask, request, jsonify
import os, uuid
from utils import verify_secret, push_to_github, post_evaluation

app = Flask(__name__)

@app.route("/api-endpoint", methods=["POST"])
def api_endpoint():
    data = request.json
    secret = data.get("secret")
    if not verify_secret(secret):
        return jsonify({"error": "Invalid secret"}), 403

    task = data.get("task")
    round_num = data.get("round", 1)
    email = data.get("email")
    nonce = data.get("nonce")
    brief = data.get("brief")
    attachments = data.get("attachments", [])

    # --- Step A: Generate / update app via LLM ---
    # For demo, just write brief to index.html
    app_folder = "app"
    os.makedirs(app_folder, exist_ok=True)
    with open(os.path.join(app_folder, "index.html"), "w", encoding="utf-8") as f:
        f.write(f"<html><body><h1>{brief}</h1></body></html>")

    # --- Step B: Push to GitHub ---
    repo_name = f"{task}"
    repo_url, commit_sha = push_to_github(repo_name, app_folder, f"Round {round_num} update")

    # --- Step C: Send evaluation POST ---
    pages_url = f"https://{os.environ['GITHUB_TOKEN'].split('_')[1]}.github.io/{repo_name}/"  # placeholder
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
