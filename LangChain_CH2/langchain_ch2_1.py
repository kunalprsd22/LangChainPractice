from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from os import environ


model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash"
)

messages = [
    SystemMessage(
        content="You are an expert Python teacher."
    ),
    HumanMessage(
        content="Explain decorators."
    )
]

messages.append(
    HumanMessage(
        content="What is FastAPI?"
    )
)

response = model.invoke(messages)

# That response is an AIMessage.
print(response.content)