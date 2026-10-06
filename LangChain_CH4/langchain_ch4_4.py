from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel,RunnablePassthrough
from os import environ


model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash"
)

# is very similar to what we'll eventually do in a real RAG application.
def get_context(question):
    return """
    FastMCP is a Python framework for building MCP servers.
    It allows developers to expose Python functions as MCP tools.
    """

prompt = ChatPromptTemplate.from_template(
    """
    Answer the question using the provided context.

    Context:
    {context}

    Question:
    {question}
    """
)

parallel = RunnableParallel(
    context=get_context,
    question=RunnablePassthrough()
)

chain = parallel | prompt | model

response = chain.invoke(
    "What is FastMCP?"
)

print(response)