import os

from google.genai import types

FILE_TEXT_LIMIT = 10000


def get_file_content(working_directory, file_path):
    try:
        if not os.path.isdir(working_directory):
            raise Exception(f'"{working_directory}" is not a directory')

        absolute_path = os.path.abspath(working_directory)
        full_path = os.path.normpath(os.path.join(absolute_path, file_path))

        if not os.path.isfile(full_path):
            raise Exception(f'File not found or is not a regular file: "{file_path}"')

        valid_path = os.path.commonpath([absolute_path, full_path]) == absolute_path

        if not valid_path:
            raise Exception(
                f'Cannot read "{file_path}" as it is outside the permitted working directory'
            )

        content = ""

        with open(full_path, "r") as file:
            first_chunk = file.read(FILE_TEXT_LIMIT)
            content += first_chunk
            if file.read(1):
                content += (
                    f'[...File "{file_path}" truncated at {FILE_TEXT_LIMIT} characters]'
                )

        return content
    except Exception as err:
        return f"Error: {err}"


# get_file_content("calculator", "main.py")

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Reads the contents of a file and returns it from the function",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the file to be read, relative to the working directory (default is the working directory itself)",
            ),
        },
        required=["file_path"],
    ),
)
