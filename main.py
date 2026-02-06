import argparse
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types


def main():
    try:
        load_dotenv()
        api_key = os.environ.get("GEMINI_API_KEY")

        if api_key is None:
            raise RuntimeError("api key not found!")

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
            model="gemini-2.5-flash",
            contents=messages,
        )

        if response.usage_metadata is None:
            raise RuntimeError("no response gotten")

        if args.verbose:
            print(f"User prompt: {args.user_prompt}")
            print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
            print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

        print(response.text)

    except RuntimeError as err:
        print(f"An error occurred: {err}")


if __name__ == "__main__":
    main()
