from langchain_core.messages import HumanMessage, AIMessage
from os import environ
from langchain_google_genai import ChatGoogleGenerativeAI

model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash"
)

messages = [
    HumanMessage(content="My name is Jacky."),
    AIMessage(content="Nice to meet you, Jacky."),
    HumanMessage(content="What is my name?")
]

response = model.invoke(messages)

print(response.content)