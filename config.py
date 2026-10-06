import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

model = ChatGoogleGenerativeAI(
     model="gemini-2.5-flash",
     google_api_key=GOOGLE_API_KEY
)