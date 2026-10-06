from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from os import environ


model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash"
)

# used to send human message only
prompt = PromptTemplate.from_template(
    """
    Explain {concept} in Python.

    Target audience: {level}

    Include:
    - Definition
    - Simple explanation
    - Python example
    - Common use case
    """
)

chain = prompt | model

response = chain.invoke({
    "concept": "decorators",
    "level": "intermediate"
})


print(response.content)