from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from os import environ

model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash"
)

# used to send system and human message both
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert Python teacher."
    ),
    (
        "human",
        "Explain {topic} in simple terms."
    )
])


chain = prompt | model


response = chain.invoke({
    "topic": "generators"
})


print(response.content)
