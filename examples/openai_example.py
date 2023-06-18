import json

import openai

from llmfuncs.tool import Tool, ToolCollection


# Define your function
def get_current_weather(location, unit="fahrenheit"):
    """Get the current weather in a given location."""
    # This is a dummy function that returns the same weather every time.
    # In a real scenario, you could call a weather API here.
    weather_info = {
        "location": location,
        "temperature": "72",
        "unit": unit,
        "forecast": ["sunny", "windy"],
    }
    return json.dumps(weather_info)


def run_conversation(model="gpt-3.5-turbo-0613"):
    # Step 1: send the conversation and available functions to GPT
    messages = [{"role": "user", "content": "What's the weather like in Boston?"}]
    tools = ToolCollection(tools=[Tool(get_current_weather)])
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        functions=tools.schema(),  # Use the schema generated from your tools
        function_call="auto",  # auto is default, but we'll be explicit
    )
    response_message = response["choices"][0]["message"]

    # Step 2: check if GPT wanted to call a function
    if response_message.get("function_call"):
        # Step 3: call the function
        function_name = response_message["function_call"]["name"]
        function_args_json = response_message["function_call"]["arguments"]
        function_response = tools.use_tool(function_name, function_args_json)

        # Step 4: send the info on the function call and function response to GPT
        messages.append(response_message)  # extend conversation with assistant's reply
        messages.append(
            {
                "role": "function",
                "name": function_name,
                "content": function_response,
            }
        )  # extend conversation with function response
        second_response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
        )  # get a new response from GPT where it can see the function response
        return second_response


print(run_conversation())
