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
    non_yaml_files_as_scalars: bool = True,
    debug: bool = False,
) -> Union[dict, list]:
    # List all files
    all_paths = [
        p for p in dir_path.glob("*")
        if not (p.is_symlink() or p.name.startswith("!"))
    ]
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

    logger.debug(f"Assembling level: {dir_path}")

    # All parsed data from index file, other yaml files, and dirs
    # will be collected into a single data object.
    data: dict = {}
    
    # Load data from the index file, if it exists
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
            data[yaml_file_name] = yaml_file_data

    # Load data from the rest of the files.
    # Example: query.sql file containing a SQL query
    for non_yaml_file_name, non_yaml_file_path in non_yaml_files.items():
        with open(non_yaml_file_path, "r") as non_yaml_file:
            non_yaml_file_content = non_yaml_file.read()
            non_yaml_node: str | FoldedScalarString = non_yaml_file_content
            if non_yaml_files_as_scalars:
                non_yaml_node = FoldedScalarString(non_yaml_file_content)
            data[non_yaml_file_name] = non_yaml_node

    # Figure out if the current folder is an array because some paths
    # within it start with the dash '-' prefix
    is_current_dir_array = any([p for p in all_paths if p.name.startswith("-")])
    logger.debug(f"Current dir contains items starting with -: {dir_path}")

    data_if_current_dir_is_array = list(data.values())
    data_if_current_dir_is_dict = data

    # Recursively traverse directories.
    # Directory's name is considered to be the name of the nested field,
    # if it's not an array. Otherwise, directory name is ignored.
    for sub_dir in all_dirs:
        sub_dir_data = assemble_recursively(sub_dir, debug=debug)

        # If directorie's name starts with a '+', then consider it a grouper
        # It doesn't represent a field. Consider data within it to be on the
        # same level as the current folder.
        is_sub_dir_grouper = sub_dir.name.startswith("+")
        is_sub_dir_array = isinstance(sub_dir_data, list)

        # If the current directory has a grouper sub directory, which in turn, is an array,
        # then the current directory is automatically considered to be an array.
        # This is because, grouping sub directories are meta-directories. It's as if they do not exist.
        # So having a grouper sub directory which is an array (because it has items that start with -)
        # means that it's actually the current directory which is an array. We just didn't know
        # until we actually traversed the sub directories of the current directory.
        is_current_dir_array = is_current_dir_array or (is_sub_dir_array and is_sub_dir_grouper)

        if is_sub_dir_grouper:
            if is_sub_dir_array:
                data_if_current_dir_is_array.extend(sub_dir_data)
            else:
                data_if_current_dir_is_dict.update(sub_dir_data)
        else:
            data_if_current_dir_is_array.append(sub_dir_data)
            data_if_current_dir_is_dict[sub_dir.name] = sub_dir_data

    logger.debug(f"Returning {'(array) ' if is_current_dir_array else ''}{dir_path}")

    if is_current_dir_array:
        return data_if_current_dir_is_array
    else:
        return data_if_current_dir_is_dict


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
