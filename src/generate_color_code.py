import json
import os

import google.generativeai as genai
import jsonschema
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

gemini = genai.GenerativeModel("gemini-pro")

json_output_prompt = """
You are an assistant designed to output json that conforms to "# json schema".
You should think of the most appropriate hexadecimal color code for the "# user prompt" and output it.
If the "# User Prompt" is not specific, choose the color that best matches that image.

Please output only json and nothing else.

# user prompt
######## user_prompt ########
{user_prompt}
######## user_prompt END ########

# json schema
######## json_schema ########
```json
{json_schema}
```
######## json_schema END ########

you should output the json that conforms to the json schema.
Please output only json and nothing else.
"""


def generate_json(prompt: str, json_schema: dict, chat, retry_num=3):
    """Generate json based on user prompt and json schema
    Args:
        prompt (str):  ユーザープロンプト
        json_schema (dict):  jsonスキーマ
        chat:  会話の履歴
        retry_num:  リトライ回数
    Returns:
        dict: 生成されたjson
    """
    if retry_num == -1:
        print("Retry limit exceeded.")
        return None
    try:
        res = chat.send_message(prompt).text
    except Exception as e:
        print(e)
        return generate_json(prompt, json_schema, chat, retry_num - 1)
    res = res.replace("json", "").replace("```", "").replace("JSON", "")
    try:
        res_json = json.loads(res)
    except json.JSONDecodeError:
        error_message = "Invalid json format. Please try again."
        print(error_message)
        print(res)
        return generate_json(error_message, json_schema, chat, retry_num - 1)

    try:
        jsonschema.validate(res_json, json_schema)
    except jsonschema.ValidationError as e:
        error_message = f"""
        Invalid json format. Please try again.

        ###### Error Message ######
        {str(e)}
        """
        print(str(e.message))
        print(res_json)
        return generate_json(error_message, json_schema, chat, retry_num - 1)

    return res_json


def generate_color_code(
    user_prompt: str, json_schema: dict, history: list = []
) -> dict:
    """Generate color code based on user prompt and json schema
    Args:
        user_prompt (str):  ユーザープロンプト
        json_schema (dict):  jsonスキーマ
        history (list, optional):  会話の履歴. Defaults to [].

    Returns:
        dict: 生成された色コード
    """
    chat = gemini.start_chat(history=history)

    prompt = json_output_prompt.format(
        user_prompt=user_prompt,
        json_schema=json.dumps(json_schema, indent=4, ensure_ascii=False),
    )

    res = generate_json(prompt, json_schema, chat)
    if res is None:
        return None

    return res
