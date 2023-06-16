import os


def write_file(filename: str, content: str) -> str:
    """
    Writes content to a file with given name. Existing files will be overwritten.

    Args:
        filename (str): The name of the file to write to.
        content (str): The content to write to the file.

    Returns:
        str: A message indicating the file was written successfully.
    """
    print(f"FUNCTION: Writing to file code/{filename}...")
    # if DEBUG: print(f"\n {content}")

    # force newline in the end
    if content[-1] != "\n":
        content = content + "\n"

    # Create parent directories if they don't exist
    parent_dir = os.path.dirname(f"code/{filename}")
    os.makedirs(parent_dir, exist_ok=True)

    with open(f"code/{filename}", "w") as f:
        f.write(content)
    return f"File {filename} written successfully"


def append_file(filename: str, content: str) -> str:
    """
    Appends content to a file.

    Args:
        filename (str): The name of the file to append to.
        content (str): The content to append to the file.

    Returns:
        str: A message indicating the file was appended successfully.
    """
    print(f"FUNCTION: Appending to file code/{filename}...")
    # if DEBUG: print(f"\n {content}")

    # Create parent directories if they don't exist
    parent_dir = os.path.dirname(f"code/{filename}")
    os.makedirs(parent_dir, exist_ok=True)

    with open(f"code/{filename}", "a") as f:
        f.write(content)
    return f"File {filename} appended successfully"


def read_file(filename: str) -> str:
    """
    Read the contents of a file with given name.

    Args:
        filename (str): The name of the file to read from.

    Returns:
        str: The contents of the file or a message indicating the file does not exist.
    """
    print(f"FUNCTION: Reading file code/{filename}...")
    if not os.path.exists(f"code/{filename}"):
        print(f"File {filename} does not exist")
        return f"File {filename} does not exist"
    with open(f"code/{filename}", "r") as f:
        content = f.read()
    return f"The contents of '{filename}':\n{content}"


def create_dir(directory: str) -> str:
    """
    Create a directory with given name.

    Args:
        directory (str): The name of the directory to create.

    Returns:
        str: A message indicating the directory was created or already exists.
    """
    print(f"FUNCTION: Creating directory code/{directory}")
    if os.path.exists("code/" + directory + "/"):
        return "ERROR: Directory exists"
    else:
        os.mkdir("code/" + directory)
        return f"Directory {directory} created!"


def delete_file(filename: str) -> str:
    """
    Deletes a file with given name.

    Args:
        filename (str): The name of the file to delete.

    Returns:
        str: A message indicating the file was deleted or does not exist.
    """
    print(f"FUNCTION: Deleting file code/{filename}")
    if not os.path.exists(f"code/{filename}"):
        print(f"File {filename} does not exist")
        return f"ERROR: File {filename} does not exist"
    os.remove(f"code/{filename}")
    return f"File {filename} successfully deleted"


def list_files() -> str:
    """
    List the files in the current project.

    Returns:
        str: A list of all files in the code directory.
    """
    files = []
    for root, _, filenames in os.walk("code/"):
        for filename in filenames:
            file_path = os.path.join(root, filename)
            files.append(file_path)
    # Remove "code/" from the beginning of file paths
    files = [file_path.replace("code/", "", 1) for file_path in files]

    print(f"FUNCTION: Files in code/ directory:\n{files}")
    return f"List of files in the project:\n{files}"


def ask_clarification(question: str) -> str:
    """
    Ask the user a clarifying question about the project.

    Args:
        question (str): The question to ask the user.

    Returns:
        str: The answer to the question.
    """
    answer = input(f"## ChatGPT Asks a Question ##\n```{question}```\nAnswer: ")
    return answer


def project_finished() -> str:
    """
    Call this function when the project is finished.

    Returns:
        str: A message indicating that the project has finished.
    """
    return "PROJECT_FINISHED"
