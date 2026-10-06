from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel
from os import environ
from langchain_core.tools import tool
from typing import List

# --------------------------------
# 1. Create a weather tool
# --------------------------------

@tool
def get_weather(city: str) -> str:
    """Get the current temperature of a city in Celsius."""

    # Normally, we would call a real weather API here.
    # For learning, we are returning fixed data.

    weather_data = {
        "Delhi": 32,
        "Mumbai": 30,
        "Bangalore": 25,
        "London": 15
    }

    temperature = weather_data.get(city)

    if temperature is None:
        return f"Weather data for {city} is not available."

    return f"The current temperature in {city} is {temperature}°C."


# --------------------------------
# 2. Create conversion tool
# --------------------------------

@tool
def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert Celsius temperature to Fahrenheit."""

    return (celsius * 9 / 5) + 32


# --------------------------------
# 3. Create Gemini
# --------------------------------

model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash"
)

# --------------------------------
# 4. Give tools to Gemini
# --------------------------------

model_with_tools = model.bind_tools([
    get_weather,
    celsius_to_fahrenheit
])

# --------------------------------
# 5. Ask Gemini
# --------------------------------

response = model_with_tools.invoke(
    "What is the current temperature in Delhi?"
)

print(response)