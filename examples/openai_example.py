import json

import openai

from llmfuncs import schema, validator


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


# Generate the schema for your function
function_schema = schema.from_function(get_current_weather)


def run_conversation(model="gpt-3.5-turbo-0613"):
    # Step 1: send the conversation and available functions to GPT
    messages = [{"role": "user", "content": "What's the weather like in Boston?"}]
    functions = [function_schema]  # Use the schema generated from your function
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        functions=functions,
        function_call="auto",  # auto is default, but we'll be explicit
    )
    response_message = response["choices"][0]["message"]

    # Step 2: check if GPT wanted to call a function
    if response_message.get("function_call"):
        # Step 3: call the function
        function_name = response_message["function_call"]["name"]
        function_args_json = response_message["function_call"]["arguments"]

        if function_name == "get_current_weather":
            # validate the arguments against the schema and call the function
            function_response = validator.validate_and_call(
                func=get_current_weather,
                args_json=function_args_json,
                schema=function_schema["parameters"],
            )

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
