from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from os import environ

model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash"
)

prompt = PromptTemplate.from_template(
    "Explain {topic} in simple terms for a beginner."
)

chain = prompt | model

response = chain.invoke({
    "topic": "FastAPI"
})


print(response.content)