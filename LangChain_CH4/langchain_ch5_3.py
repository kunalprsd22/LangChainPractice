from langchain_core.runnables import RunnableParallel

chain = RunnableParallel(
    original=lambda x: x,
    uppercase=lambda x: x.upper(),
    length=lambda x: len(x)
)

result = chain.invoke("FastMCP")

print(result)