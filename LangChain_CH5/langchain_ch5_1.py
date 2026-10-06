from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from os import environ


model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash"
)

response = model.invoke(
    "what is python?"
)

parser = StrOutputParser()

parser_result =  parser.invoke(response)

print(parser_result)