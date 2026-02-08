import os
import subprocess


def run_python_file(working_directory, file_path, args=None):
    try:
        absolute_path = os.path.abspath(working_directory)
        full_path = os.path.normpath(os.path.join(absolute_path, file_path))
        valid_path = os.path.commonpath([absolute_path, full_path]) == absolute_path

        if not valid_path:
            raise Exception(
                f'Cannot execute "{file_path}" as it is outside the permitted working directory'
            )

        if not os.path.isfile(full_path):
            raise Exception(f'"{file_path}" does not exist or is not a regular file')

        if not file_path.endswith(".py"):
            raise Exception(f'"{file_path}" is not a Python file')

        command = ["python", full_path]
        if args:
            command.extend(args)

        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        output = ""

        if result.returncode != 0:
            output = f"Process exited with code {result.returncode}"
        elif not result.stdout and not result.stderr:
            output = "No output produced"
        elif result.stdout or result.stderr:
            if result.stdout:
                output += f"STDOUT: {result.stdout}\n"
            if result.stderr:
                output += f"STDERR: {result.stderr}\n"

        print(output)
        return output

    except Exception as err:
        print(f"Error: executing Python file: {err}")


# run_python_file("calculator", "lorem.txt")
