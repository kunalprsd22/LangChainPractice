from langchain_google_genai import ( GoogleGenerativeAIEmbeddings )
from langchain_chroma import Chroma
from langchain_text_splitters import ( RecursiveCharacterTextSplitter)
from os import environ

company_policy = """
Company Leave Policy

Employees receive the following leave every year.

Casual Leave:
12 days per year.

Sick Leave:
10 days per year.

Earned Leave:
15 days per year.

Casual leave can be carried forward up to
5 days to the next year.

Sick leave cannot be carried forward.

Earned leave can be carried forward according
to company policy.

Employees should apply for leave through
the company's HR system.

Employees must have sufficient leave balance
before applying for leave.

Leave applications that change employee records
require appropriate authorization.
"""


def create_retriever():

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50
    )

    documents = text_splitter.create_documents(
        [company_policy]
    )

    embeddings = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001"
    )

    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name="employee_leave_policy"
    )

    retriever = vector_store.as_retriever(
        search_kwargs={
            "k": 3
        }
    )

    return retriever