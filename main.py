import argparse
import os
import sys

from dotenv import load_dotenv
from google import genai
from google.genai import types

from call_function import available_functions, call_function
from prompts import system_prompt


def run_fn_loop(client, model_name, args, messages):
    response = client.models.generate_content(
        model=model_name,
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions], system_instruction=system_prompt
        ),
    )
    print(response)
    function_calls = []
    response_text = None

    if not response.candidates:
        response_text = "Error: No candidates returned."

    parts = response.candidates[0].content.parts
    if not parts:
        response_text = "Loop ended"

    if response.candidates is not None and len(response.candidates):
        for candidate in response.candidates:
            messages.append(candidate.content)
            if candidate.content.parts and len(candidate.content.parts):
                function_calls.append(candidate.content.parts[0].function_call)
                response_text = candidate.content.parts[0].text

    if response.usage_metadata is None:
        raise RuntimeError("no response gotten")

    if args.verbose:
        print(f"User prompt: {args.user_prompt}")
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

    function_results = []
    loop_response = {}

    loop_response["response_text"] = response_text

    if response_text is not None:
        return loop_response

    # print(function_calls)
    # print(response_text)
    if len(function_calls):
        for fn_call in function_calls:
            function_call_result = call_function(fn_call, args.verbose)
            if (
                function_call_result.parts is None
                or function_call_result.parts[0].function_response is None
                or function_call_result.parts[0].function_response.response is None
            ):
                raise Exception(f"An error occurred while calling {fn_call.name}")

            if args.verbose:
                print(f"-> {function_call_result.parts[0].function_response.response}")

            function_results.append(function_call_result.parts[0])

    messages.append(types.Content(role="user", parts=function_results))

    loop_response["messages"] = messages

    return loop_response


def main():
    try:
        load_dotenv()
        api_key = os.environ.get("GEMINI_API_KEY")
        model_name = os.environ.get("MODEL_NAME")

        if api_key is None:
            raise RuntimeError("api key not found!")

        if model_name is None:
            raise RuntimeError("invalid model provided!")

        client = genai.Client(api_key=api_key)

        parser = argparse.ArgumentParser(description="Ask me anything")
        parser.add_argument("user_prompt", type=str, help="User prompt")
        parser.add_argument(
            "--verbose", "-v", action="store_true", help="Enable verbose output"
        )
        args = parser.parse_args()

        messages = [
            types.Content(role="user", parts=[types.Part(text=args.user_prompt)])
        ]

        for i in range(20):
            # print(messages)
            res = run_fn_loop(client, model_name, args, messages)
            if res["response_text"] is not None:
                print(res["response_text"])
                break
            else:
                messages.extend(res["messages"])
                if i == 20:
                    print("Loop terminated. Maximum number of steps reached.")
                    sys.exit(1)

    except RuntimeError as err:
        print(f"An error occurred: {err}")


if __name__ == "__main__":
    main()
