# Reference: https://platform.openai.com/docs/guides/function-calling
import json
import os

from qwen_agent.llm import get_chat_model


# Example dummy function hard coded to return the same weather
# In production, this could be your backend API or an external API
def get_current_weather(location, unit="摄氏度"):
    """获取给定位置的当前天气"""
    if "北京" in location:
        return json.dumps({"location": "北京", "temperature": "32", "unit": "摄氏度"})
    elif "保定市" in location:
        return json.dumps({"location": "保定市", "temperature": "28", "unit": "摄氏度"})
    elif "南京市" in location.lower():
        return json.dumps({"location": "南京市", "temperature": "22", "unit": "摄氏度"})
    else:
        return json.dumps({"location": location, "temperature": "unknown"})


def test():
    key = os.getenv("DASHSCOPE_API_KEY")

    print("key", key)
    llm = get_chat_model(
        {
            # Use the model service provided by DashScope:
            "model": "qwen2-1.5b-instruct",
            "model_server": "dashscope",
            # "api_key": os.getenv("DASHSCOPE_API_KEY"),
            "api_key": "sk-cd8f0b15a37f47729f2dc7bba934c587",
            # Use the model service provided by Together.AI:
            # 'model': 'Qwen/Qwen1.5-14B-Chat',
            # 'model_server': 'https://api.together.xyz',  # api_base
            # 'api_key': os.getenv('TOGETHER_API_KEY'),
            # Use your own model service compatible with OpenAI API:
            # 'model': 'Qwen/Qwen1.5-72B-Chat',
            # 'model_server': 'http://localhost:8000/v1',  # api_base
            # 'api_key': 'EMPTY',
            # "model": "qwen2:latest",
            # "model_server": "http://localhost:11434/v1",
            # "api_key": "111",
        }
    )

    # Step 1: send the conversation and available functions to the model
    messages = [{"role": "user", "content": "北京的天气怎么样?"}]
    functions = [
        {
            "name": "get_current_weather",
            "description": "获取给定位置的当前天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "城市,例如:北京市,河北省保定市",
                    },
                    # "unit": {"type": "string", "enum": ["摄氏度", "华氏度"]},
                },
                "required": ["location"],
            },
        }
    ]

    print("# Assistant Response 1:")
    responses = []
    for responses in llm.chat(messages=messages, functions=functions, stream=True):
        print(1111, responses)

    messages.extend(
        responses
    )  # extend conversation with assistant's reply 通过助理的回复扩展对话

    # Step 2: check if the model wanted to call a function 检查模型是否想要调用函数
    last_response = messages[-1]
    if last_response.get("function_call", None):

        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "get_current_weather": get_current_weather,
        }  # only one function in this example, but you can have multiple
        function_name = last_response["function_call"]["name"]
        function_to_call = available_functions[function_name]
        function_args = json.loads(last_response["function_call"]["arguments"])

        # 查询北京的天气
        function_response = function_to_call(
            location=function_args.get("location"),
            unit=function_args.get("unit"),
        )
        print("# Function Response:")
        print(function_response)

        # Step 4: send the info for each function call and function response to the model 将每个函数调用和函数响应的信息发送给模型
        messages.append(
            {
                "role": "function",
                "name": function_name,
                "content": function_response,
            }
        )  # extend conversation with function response

        print("# Assistant Response 2:")
        for responses in llm.chat(
            messages=messages,
            functions=functions,
            stream=True,
        ):  # get a new response from the model where it can see the function response
            print(responses)


if __name__ == "__main__":
    test()
