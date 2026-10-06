from config import model

option = 1

if option == 1:
  # invoke :- Send this input to the model and return the result.
  response = model.invoke(
    "What is Python?"
  )
  print(response.content)
elif option == 2:
   # One input → response chunks
   for chunk in model.stream("Tell me a story"):
    print(chunk.content, end="")
elif option == 3:
  # Multiple inputs → multiple responses
  responses = model.batch([
    "What is Python?",
    "What is FastAPI?",
    "What is MCP?"
 ])


