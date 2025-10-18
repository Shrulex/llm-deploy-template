from flask import Flask, request, jsonify
from utils import verify_secret, generate_app_from_brief, push_files_to_github, post_evaluation
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret')


@app.route("/api-endpoint", methods=["POST"])
def api_endpoint():
    try:
        data = request.get_json(force=True)
        email = data.get("email")
        secret = data.get("secret")
        task = data.get("task")
        round_number = data.get("round")
        nonce = data.get("nonce")
        brief = data.get("brief")
        attachments = data.get("attachments", [])

        # Verify secret
        if not verify_secret(secret):
            return jsonify({"error": "Invalid secret"}), 403

        # Generate app files from brief
        files = generate_app_from_brief(brief, attachments)

        # Push files to GitHub
        repo_url = push_files_to_github(files, task)

        # Notify evaluation API
        eval_response = post_evaluation(repo_url, email, task, round_number, nonce)

        return jsonify({
            "message": "Task processed successfully",
            "repo_url": repo_url,
            "evaluation_response": eval_response
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/", methods=["GET"])
def index():
    return "LLM Deploy API is running!"


if __name__ == "__main__":
    host = os.environ.get("FLASK_RUN_HOST", "0.0.0.0")
    port = int(os.environ.get("FLASK_RUN_PORT", 5000))
    app.run(host=host, port=port)
