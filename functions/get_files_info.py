import os


def get_files_info(working_directory, directory="."):
    try:
        if not os.path.isdir(working_directory):
            raise Exception(f'"{working_directory}" is not a directory')

        absolute_path = os.path.abspath(working_directory)
        full_path = os.path.normpath(os.path.join(absolute_path, directory))

        if not os.path.isdir(full_path):
            raise Exception(f'"{full_path}" is not a directory')

        valid_path = os.path.commonpath([absolute_path, full_path]) == absolute_path

        if not valid_path:
            raise Exception(
                f'Cannot list "{directory}" as it is outside the permitted working directory'
            )

        files_info = []
        for file in os.listdir(full_path):
            file_path = os.path.normpath(os.path.join(full_path, file))
            files_info.append(
                f"- {file}: file_size={os.path.getsize(file_path)}, is_dir={os.path.isdir(file_path)}"
            )

        return "\n".join(files_info)
    except Exception as err:
        return f"Error: {err}"


# get_files_info("calculator", "pkg")
