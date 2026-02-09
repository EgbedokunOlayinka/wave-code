import os

from google.genai import types


def write_file(working_directory, file_path, content):
    try:
        if not os.path.isdir(working_directory):
            os.makedirs(working_directory, exist_ok=True)

        absolute_path = os.path.abspath(working_directory)
        full_path = os.path.normpath(os.path.join(absolute_path, file_path))

        if os.path.isdir(full_path):
            raise Exception(f'Cannot write to "{file_path}" as it is a directory')

        valid_path = os.path.commonpath([absolute_path, full_path]) == absolute_path

        if not valid_path:
            raise Exception(
                f'Cannot write to "{file_path}" as it is outside the permitted working directory'
            )

        with open(full_path, "w") as file:
            file.write(content)
        return (
            f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
        )

    except Exception as err:
        return f"Error: {err}"


# write_file("calculator", "pkg/morelorem.txt", "lorem ipsum dolor sit amet")

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes some content to a file and returns a success message after completion",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the file to be written to, relative to the working directory (default is the working directory itself)",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="Content to be written to the file",
            ),
        },
        required=["file_path", "content"],
    ),
)
