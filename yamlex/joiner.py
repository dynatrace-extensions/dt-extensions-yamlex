import logging
from pathlib import Path
from typing import Union

import ruamel.yaml
from ruamel.yaml.scalarstring import FoldedScalarString


logger = logging.getLogger(__name__)
parser = ruamel.yaml.YAML()


# How joiner works
# - The goal is to recreate the YAML structure of the extension.yaml from files
# - All files with *.yaml extension are considered
# - We start to rebuild from the same level where extension.yaml is. Loop:


def assemble_recursively(
    dir_path: Path,
    non_yaml_files_as_multiline_string: bool = True,
    debug: bool = False,
) -> Union[dict, list]:
    # List all files
    all_paths = [p for p in dir_path.glob("*") if not p.is_symlink()]
    all_dirs: list[Path] = []
    all_yamls: dict[str, Path] = {}
    non_yaml_files: dict[str, Path] = {}
    for p in all_paths:
        if p.is_dir():
            all_dirs.append(p)
        elif p.is_file():
            if p.suffix in (".yaml", ".yml"):
                all_yamls[p.stem] = p
            else:
                non_yaml_files[p.stem] = p

    # Figure out if the current folder is an array
    is_array = any([p for p in all_paths if p.name.startswith("-")])
    logger.debug(f"Assembling {'(array)' if is_array else ''} level: {dir_path}")

    # All parsed data from index file, other yaml files, and dirs
    # will be collected into a single data object.
    data: Union[dict, list] = [] if is_array else {}
    
    # Load data from the index file, if it exists
    if not is_array:
        if "index" in all_yamls:
            index_yaml_file_path = all_yamls.pop("index")
            with open(index_yaml_file_path, "r") as index_yaml_file:
                # index_yaml_file_data = yaml.safe_load(index_yaml_file)
                index_yaml_file_data = parser.load(index_yaml_file)
                data.update(index_yaml_file_data)

    # Load data from the rest of the YAML files.
    # File's name is considered to be the name of the nested field,
    # if it's not an array. Otherwise, file name is ignored completely
    for yaml_file_name, yaml_file_path in all_yamls.items():
        with open(yaml_file_path, "r") as yaml_file:
            # yaml_file_data = yaml.safe_load(yaml_file)
            yaml_file_data = parser.load(yaml_file)

            if is_array:
                data.append(yaml_file_data)
            else:
                data[yaml_file_name] = yaml_file_data

    # Load data from the rest of the files.
    # Example: query.sql file containing a SQL query
    for non_yaml_file_name, non_yaml_file_path in non_yaml_files.items():
        with open(non_yaml_file_path, "r") as non_yaml_file:
            non_yaml_file_content = non_yaml_file.read()
            non_yaml_node: str | FoldedScalarString = non_yaml_file_content
            if non_yaml_files_as_multiline_string:
                non_yaml_node = FoldedScalarString(non_yaml_file_content)

            if is_array:
                data.append(non_yaml_node)
            else:
                data[non_yaml_file_name] = non_yaml_node

    # Recursively traverse directories.
    # Directorie's name is considered to be the name of the nested field,
    # if it's not an array. Otherwise, directory name is ignored.
    for dir in all_dirs:
        dir_data = assemble_recursively(dir, debug=debug)

        # If directorie's name starts with a '+', then consider it a grouper
        # It doesn't represent a field. Consider data within it to be on the
        # same level as the current folder.
        # Does not apply if the current folder is considered to be an array.
        is_grouper = dir.name.startswith("+")

        if is_array:
            if is_grouper:
                data.extend(dir_data)
            else:
                data.append(dir_data)
        else:
            if is_grouper:
                data.update(dir_data)
            else:
                data[dir.name] = dir_data

    return data


def remove_yaml_comments(data: Union[dict, list]):
    if hasattr(data, 'ca'):
        # Remove comments associated with this node
        data.ca.comment = None
        
        if hasattr(data.ca.items, 'items'):
            for key in data.ca.items:
                # Remove key comments
                data.ca.items[key] = [None, None, None, None]

    if isinstance(data, dict):
        for value in data.values():
            remove_yaml_comments(value)
            
    elif isinstance(data, list):
        for item in data:
            remove_yaml_comments(item)
