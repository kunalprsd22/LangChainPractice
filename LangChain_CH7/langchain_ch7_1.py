from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain.agents import create_agent
from os import environ


# --------------------------------
# Tool 1: Weather
# --------------------------------

@tool
def get_weather(city: str) -> str:
    """Get the current temperature of a city in Celsius."""

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
# Tool 2: Temperature conversion
# --------------------------------

@tool
def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert Celsius temperature to Fahrenheit."""

    return (celsius * 9 / 5) + 32


# --------------------------------
# Gemini
# --------------------------------

model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash"
)


# --------------------------------
# Agent
# --------------------------------

agent = create_agent(
    model=model,
    tools=[
        get_weather,
        celsius_to_fahrenheit
    ]
)


# --------------------------------
# Ask the agent
# --------------------------------

response = agent.invoke({
    "messages": [
        {
            "role": "user",
            "content":
                "What is the current temperature in Delhi "
                "in Fahrenheit?"
        }
    ]
})


# --------------------------------
# Print messages
# --------------------------------

for message in response["messages"]:
    print("\n---")
    print(message)