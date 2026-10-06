from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from os import environ

model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash"
)

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

parser = StrOutputParser()

chain = prompt | model | parser

response = chain.invoke({
    "topic": "generators"
})


print(response)