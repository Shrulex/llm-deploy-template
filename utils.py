# utils.py
import os
import openai

# Make sure your OPENAI_API_KEY is set in environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_app_from_brief(brief, attachments=None):
    """
    Generates a simple app or code snippet from the brief using OpenAI's GPT-4.
    
    :param brief: String describing what the app/page should do
    :param attachments: List of attachments (not used currently)
    :return: Generated code string
    """

    # Fallback for attachments if None
    if attachments is None:
        attachments = []

    try:
        # New OpenAI API syntax
        response = openai.chat.completions.create(
            model="gpt-4",  # You can also use "gpt-3.5-turbo"
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that writes complete HTML/CSS/JS web pages based on user briefs."
                },
                {
                    "role": "user",
                    "content": brief
                }
            ],
            temperature=0  # Deterministic output
        )

        # Extract the generated code from the response
        code = response.choices[0].message.content

        # For now, return as a list to mimic multiple files if needed
        return [{"filename": "index.html", "content": code}]

    except Exception as e:
        print("Error generating app:", e)
        return [{"filename": "error.txt", "content": str(e)}]
