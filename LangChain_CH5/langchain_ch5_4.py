from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel
from os import environ
from typing import List


class DeveloperProfile(BaseModel):
    role: str
    primary_language: str
    experience_level: str
    technologies: list[str]
    recommended_next_skill: str

model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash"
)

structured_model = model.with_structured_output(DeveloperProfile)

result = structured_model.invoke(
    """
    Analyze this developer:

    They know:
    - iOS
    - Swift
    - Python
    - FastAPI
    - FastMCP
    - LangChain

    They want to work on AI applications.
    """
)

print(result)