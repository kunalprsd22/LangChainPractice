from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.messages import HumanMessage, AIMessage
from os import environ
from langchain_google_genai import ChatGoogleGenerativeAI


model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash"
)

history = []

# First question
user_message = HumanMessage(
    content="My name is Jacky and I am an iOS developer."
)

history.append(user_message)

response = model.invoke(history)

print("AI:", response.content)

history.append(
    AIMessage(content=response.content)
)

# Second question
user_message = HumanMessage(
    content="What is my profession?"
)

history.append(user_message)

response = model.invoke(history)

print("AI:", response.content)