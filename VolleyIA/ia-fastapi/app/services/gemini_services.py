import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from app.prompts.system_prompt import SYSTEM_PROMPT

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def preguntar_a_gemini(contexto: str):

    respuesta = client.models.generate_content(

        model="gemini-2.0-flash",

        contents=contexto,

        config=types.GenerateContentConfig(

            temperature=0.7,

            top_p=0.95,

            top_k=40,

            max_output_tokens=4000,

            candidate_count=1

        )

    )

    return respuesta.text.strip()