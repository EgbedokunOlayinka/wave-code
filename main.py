import argparse
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from call_function import available_functions, call_function
from prompts import system_prompt


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

        response = client.models.generate_content(
            model=model_name,
            contents=messages,
            config=types.GenerateContentConfig(
                tools=[available_functions], system_instruction=system_prompt
            ),
        )

        if response.usage_metadata is None:
            raise RuntimeError("no response gotten")

        if args.verbose:
            print(f"User prompt: {args.user_prompt}")
            print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
            print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

        function_results = []

        if response.function_calls is not None:
            for fn_call in response.function_calls:
                # print(f"Calling function: {fn_call.name}({fn_call.args})")
                function_call_result = call_function(fn_call, args.verbose)
                if (
                    function_call_result.parts is None
                    or function_call_result.parts[0].function_response is None
                    or function_call_result.parts[0].function_response.response is None
                ):
                    raise Exception(f"An error occurred while calling {fn_call.name}")

                if args.verbose:
                    print(
                        f"-> {function_call_result.parts[0].function_response.response}"
                    )

                function_results.append(function_call_result.parts[0])

        else:
            print(response.text)

    except RuntimeError as err:
        print(f"An error occurred: {err}")


if __name__ == "__main__":
    main()
