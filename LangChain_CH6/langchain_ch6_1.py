from langchain_google_genai import (ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings)
from os import environ
from langchain_chroma import Chroma
from langchain_text_splitters import (RecursiveCharacterTextSplitter)
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import (RunnableParallel,RunnablePassthrough)

# --------------------------------
# 1. Our document
# --------------------------------

document = """
FastAPI is a modern Python web framework.

FastAPI is commonly used to build REST APIs and backend services.

FastAPI uses Python type hints and Pydantic for data validation.

FastMCP is a Python framework for building MCP servers.

FastMCP allows developers to expose Python functions as MCP tools.

LangChain is a framework for building applications powered by language models.

LangChain provides components for prompts, models, retrievers, tools and agents.
"""


# --------------------------------
# 2. Split document
# --------------------------------

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=30
)

chunks = text_splitter.create_documents(
    [document]
)


# --------------------------------
# 3. Create embeddings
# --------------------------------

embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001"
)


# --------------------------------
# 4. Create vector store
# --------------------------------

vector_store = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings
)


# --------------------------------
# 5. Create retriever
# --------------------------------

retriever = vector_store.as_retriever(
    search_kwargs={"k": 2}
)


# --------------------------------
# 6. Gemini
# --------------------------------

model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash"
)


# --------------------------------
# 7. Prompt
# --------------------------------

prompt = ChatPromptTemplate.from_template(
    """
    Answer the question using only the provided context.

    If the answer is not present in the context,
    say that you don't know.

    Context:
    {context}

    Question:
    {question}
    """
)


# --------------------------------
# 8. RAG Chain
# --------------------------------

rag_chain = (
    RunnableParallel(
        context=retriever,
        question=RunnablePassthrough()
    )
    | prompt
    | model
)


# --------------------------------
# 9. Ask question
# --------------------------------

# question = "What is FastMCP?"
question = "Who invented Java?"

response = rag_chain.invoke(question)

print(response.content)