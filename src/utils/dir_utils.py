import os
from pathlib import Path
from typing import List, Optional


def list_files_by_extension(directory: str, extension: str, recursive: bool = False) -> List[str]:

    if extension.startswith('.'):
        extension = extension[1:]
    
    if not os.path.exists(directory):
        raise FileNotFoundError(f'O diretório "{directory}" não existe.')
    
    result_files = []
    
    dir_path = Path(directory)
    
    if recursive:
        pattern = f'**/*.{extension}'
    else:
        pattern = f'*.{extension}'
    
    for file_path in dir_path.glob(pattern):
        if file_path.is_file():
            result_files.append(str(file_path))
    
    return result_files


def get_subdirectories(directory: str) -> List[str]:

    if not os.path.exists(directory):
        raise FileNotFoundError(f'O diretório "{directory}" não existe.')
    
    subdirs = []
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            subdirs.append(item_path)
    
    return subdirs


def ensure_directory_exists(directory: str) -> None:

    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
