import json
import re
import ast
from tenacity import retry, stop_after_attempt, wait_exponential
import openai

USER_AGENT = 'NameDetailsBot/0.0 (https://todo.ai/NameDetailsBot/'


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def openai_call(**kwargs):
    return openai.ChatCompletion.create(**kwargs)
def process_json_str(json_str):
    # Step 1: Direct JSON loading
    try:
        result = json.loads(json_str)
        print("Successfully processed as a valid JSON string.")
        return result
    except json.JSONDecodeError:
        print("Not a valid JSON string.")

    # Step 2: Handling triple back-ticks
    if '```' in json_str:
        print("Attempting to process as a JSON string wrapped in triple back-ticks...")
        try:
            json_str = re.search('```(.*?)```', json_str, re.DOTALL).group(1)
            result = json.loads(json_str)
            print("Successfully processed JSON string.")
            return result
        except:
            print("Failed to process as a JSON string wrapped in triple back-ticks.")

    # Step 3: Handling escape characters
    if '\\' in json_str:
        print("Attempting to process as a JSON string with escape characters...")
        try:
            json_str = json_str.encode("utf-8").decode("unicode_escape")
            result = json.loads(json_str)
            print("Successfully processed JSON string.")
            return result
        except:
            print("Failed to process as a JSON string with escape characters.")

    # Step 4: Replacing ' with "
    if "'" in json_str:
        print("Attempting to process as a JSON string with single quotes...")
        try:
            json_str = re.sub("(?<=[:\[,])\s*'|\s*'(?=[,\]})", '"', json_str)
            result = json.loads(json_str)
            print("Successfully processed JSON string.")
            return result
        except:
            print("Failed to process as a JSON string with single quotes.")

    # Step 5: Using ast.literal_eval() as a last resort
    print("Attempting to process with ast.literal_eval()...")
    try:
        result = ast.literal_eval(json_str)
        print("Successfully processed JSON string.")
        return result
    except:
        print("Failed to process with ast.literal_eval(). All attempts to process the JSON string have failed.")
        return None