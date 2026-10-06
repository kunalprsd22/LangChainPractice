import asyncio
from langchain_google_genai import ( ChatGoogleGenerativeAI,GoogleGenerativeAIEmbeddings)
from langchain_chroma import Chroma
from langchain_text_splitters import ( RecursiveCharacterTextSplitter )
from langchain_core.tools import tool
from langchain_mcp_adapters.client import ( MultiServerMCPClient )
from langchain.agents import create_agent
from os import environ

# --------------------------------------------------
# 1. COMPANY POLICY DOCUMENT
# --------------------------------------------------


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
"""

# --------------------------------------------------
# 2. CREATE DOCUMENT CHUNKS
# --------------------------------------------------

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=50
)

documents = text_splitter.create_documents(
    [company_policy]
)

# --------------------------------------------------
# 3. CREATE GEMINI EMBEDDINGS
# --------------------------------------------------

embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001"
)

# --------------------------------------------------
# 4. CREATE CHROMA VECTOR DATABASE
# --------------------------------------------------

vector_store = Chroma.from_documents(
    documents=documents,
    embedding=embeddings,
    collection_name="company_leave_policy"
)

# --------------------------------------------------
# 5. CREATE RETRIEVER
# --------------------------------------------------

retriever = vector_store.as_retriever(
    search_kwargs={"k": 3}
)


# --------------------------------------------------
# 6. TURN RAG RETRIEVER INTO A TOOL
# --------------------------------------------------

@tool
def search_leave_policy(question: str) -> str:
    """
    Search the company leave policy documents.

    Use this tool whenever the user asks about:
    leave policy, leave rules, carry forward,
    eligibility, or company leave guidelines.
    """

    documents = retriever.invoke(question)

    if not documents:
        return "No relevant leave policy information was found."

    return "\n\n".join(
        document.page_content
        for document in documents
    )


# --------------------------------------------------
# 7. MAIN
# --------------------------------------------------

async def main():
    # ----------------------------------------------
    # MCP CLIENT
    # ----------------------------------------------

    client = MultiServerMCPClient(
        {
            "hr_server": {
                "transport": "http",
                "url": "http://127.0.0.1:8000/mcp"
            }
        }
    )

    # ----------------------------------------------
    # GET MCP TOOLS
    # ----------------------------------------------

    mcp_tools = await client.get_tools()

    print("\nMCP TOOLS:")

    for tool_item in mcp_tools:
        print("-", tool_item.name)

    # ----------------------------------------------
    # GEMINI
    # ----------------------------------------------

    model = ChatGoogleGenerativeAI(
        model="gemini-3.6-flash"
    )

    # ----------------------------------------------
    # COMBINE:
    #
    # RAG TOOL
    # +
    # MCP TOOLS
    # ----------------------------------------------

    tools = [
        search_leave_policy,
        *mcp_tools
    ]

    # ----------------------------------------------
    # CREATE AGENT
    # ----------------------------------------------

    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt="""
        You are an employee HR assistant.

        You have access to two types of capabilities:

        1. search_leave_policy
           - Use this for company leave policies,
             rules, carry-forward rules and guidelines.

        2. MCP HR tools
           - Use these for current employee information,
             such as leave balances.

        When a question requires both company policy
        and current employee information, use both
        capabilities.

        Do not invent employee data.

        Give a clear and concise answer.
        """
    )

    # ----------------------------------------------
    # ASK THE AGENT
    # ----------------------------------------------

    response = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "My employee ID is EMP002. "
                        "How many casual leaves do I have "
                        "and how many can I carry forward?"
                    )
                }
            ]
        }
    )

    # ----------------------------------------------
    # PRINT FINAL RESPONSE
    # ----------------------------------------------

    print("\n\nFINAL ANSWER:")
    content = response["messages"][-1].content

    if isinstance(content, list):
        for item in content:
            if item.get("type") == "text":
                print(item["text"])
    else:
        print(content)


if __name__ == "__main__":
    asyncio.run(main())