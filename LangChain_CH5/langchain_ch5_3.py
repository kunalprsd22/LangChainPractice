from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel
from os import environ
from typing import List


class Technology(BaseModel):
    name: str
    language: str
    type: str
    difficulty: str
    use_cases: List[str]

model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash"
)

structured_model = model.with_structured_output(Technology)

prompt = ChatPromptTemplate.from_template(
    """
    Analyze the following technology.

    Technology:
    {technology}

    Return information according to the required structure.
    """
)


chain = prompt | structured_model

result = chain.invoke({
    "technology":  "FastAPI",
})

print(result)