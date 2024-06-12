import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

class GeminiQuery:
    queryText: str

    genai.configure(api_key="")
    # replace above with your API key. For more information see Gemini Docs.

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash"
    )

    chat_session = model.start_chat(
    history=[
        {
        "role": "user",
        "parts": [
            "You are an expert mass spectrometry analyst. Your job is to review plaintext documents in which there are tables, extract just the tables, and rewrite these tables as CSV files. After generating the CSV, provide the result as the CSV content with commas as the delimiter and values enclosed in double-quotes. The next messages will contain the plaintext. Respond after each one.",
        ],
        },
        {
        "role": "model",
        "parts": [
            "Understood. I'm ready to analyze your plaintext documents and extract tables into CSV format. Please provide the first document. \n",
        ],
        },
    ]
    )

    def newCSVQuery (self) -> str :

        response = self.chat_session.send_message(self.queryText, safety_settings={
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE
        })

        return response.text