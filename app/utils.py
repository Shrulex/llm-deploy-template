import openai
import base64
import os

openai.api_key = os.environ.get("OPENAI_API_KEY")

def generate_app_from_brief(brief, attachments=[]):
    """
    Generates minimal HTML/CSS/JS app using LLM.
    attachments: list of {"name": ..., "url": ...} (data URI)
    """
    attachment_text = ""
    for a in attachments:
        if a["url"].startswith("data:text") or a["url"].startswith("data:image"):
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
        # fallback
        return [{"path": "index.html", "content": f"<html><body><h1>{brief}</h1></body></html>"}]
