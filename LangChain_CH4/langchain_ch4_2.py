from langchain_core.runnables import RunnableParallel, RunnablePassthrough

#Whatever input I receive, put it into question unchanged.
chain = RunnableParallel(
    question=RunnablePassthrough(),
    length=lambda x: len(x)
)


result = chain.invoke("What is FastMCP?")

print(result)