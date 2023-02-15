from typing import List
from pathlib import Path


def find_files(extension: str, paths: List[Path], recursive: bool = False) -> List[Path]:
    """
    Finds files with the specified extension in the specified paths and returns them as  a list.
    :param extension: The extension of the file, starts with a '.' (e.g. '.png')
    :param paths:  A list of Path objects pointing to specific files, or directories to search.
    :param recursive: Flag to indicate if the directory search should be recursive or not.
    :return: A list of valid Path objects.
    """
    if not extension.startswith("."):
        extension = "." + extension
    file_paths = []
    for path in paths:
        if not path.exists():
            print(f"Could not find {path}.")
            continue
        if path.is_dir():
            file_paths.extend(path.rglob(f"*{extension}")) if recursive else file_paths.extend(path.glob(f"*{extension}"))
        elif path.is_file():
            if path.suffix != extension:
                print(f"Not a {extension} file: {path}.")
                continue
            file_paths.append(path)
        else:
            print(f"Not a file or directory: {path}")
            continue
    return file_paths
