import sys
import logging
import warnings
from pathlib import Path
from typing import Union

import ruamel.yaml
from ruamel.yaml.scalarstring import FoldedScalarString
from ruamel.yaml.comments import (
    CommentedBase,
    CommentedMap,
    CommentedSeq,
    Comment,
)

from .util import remove_yaml_comments, indent as indentation
from .exceptions import (
    InvalidItemWithinArrayDirectoryError,
    UnintendedIndexFileWarning,
    NonTextFileError,
    FailedToParseYamlError,
    IndexFileIsArray,
    DuplicateKey,
)


logger = logging.getLogger(__name__)
parser = ruamel.yaml.YAML()


def assemble_recursively(
    dir_path: Path,
    keep_formatting: bool = True,
    sort_paths: bool = False,
    dry_run: bool = False,
    remove_comments: bool = False,
    level: int = 0,
) -> Union[dict, list]:
    indent = indentation(level)
    logger.debug(f"{indent}Assembling level: {dir_path}")

    # Get all files in this directory that we will process, but ignore
    # symlinks and paths starting with '!'
    all_paths = [
        p for p in dir_path.glob("*")
        if not (p.is_symlink() or p.name.startswith("!"))
    ]

    # Enable alphabetically sorted keys for fancy users
    if sort_paths:
        all_paths.sort(key=lambda p: p.name)

    # We deal with three types of paths within the directory:
    # 1. Directories
    all_dirs: list[Path] = []
    # 2. YAML files
    all_yamls: dict[str, Path] = {}
    # 3. Non-YAML scalar files, such as SQL queries, DQL, text files, etc.
    scalar_files: dict[str, Path] = {}
    for p in all_paths:
        if p.is_dir():
            all_dirs.append(p)
        elif p.is_file():
            if p.suffix in (".yaml", ".yml"):
                all_yamls[p.stem] = p
            else:
                scalar_files[p.stem] = p

    # All parsed data will be collected into a single data object.
    # However, we don't know in advance, whether we are dealing with
    # a dictionary or a list.
    data: dict[str, Union[dict, list, str, FoldedScalarString]] = {}

    # Parse data from YAML files.
    for yaml_file_name, yaml_file_path in all_yamls.items():
        with open(yaml_file_path, "r") as yaml_file:
            try:
                yaml_file_data = parser.load(yaml_file)
            except Exception as e:
                raise FailedToParseYamlError(
                    f"Failed to parse {yaml_file_path} in {dir_path}. "
                    "Please make sure the YAML syntax is correct. "
                    f"The exact parsing error is: {e}"
                )
            
            if yaml_file_name in data:
                raise DuplicateKey(
                    f"Duplicate key found inside {dir_path}: {yaml_file_name}"
                )
            
            # Remove comments if necessary
            data[yaml_file_name] = remove_yaml_comments(
                yaml_file_name,
                yaml_file_data,
                recursive=True,
                level=level + 1,
            ) if remove_comments else yaml_file_data

    # Load data from scalar files.
    # Example: query.sql file containing a SQL query
    for scalar_file_name, scalar_file_path in scalar_files.items():
        with open(scalar_file_path, "r") as scalar_file:
            try:
                scalar_file_content = scalar_file.read()
            except UnicodeDecodeError:
                raise NonTextFileError((
                    f"Non-text file {scalar_file_path} found in {dir_path}. "
                    "Only plain text files and folders can be read by "
                    "yamlex. To ignore the file, prefix it with an "
                    f"exclamation mark like so: !{scalar_file_name}."
                ))
            scalar_node: str | FoldedScalarString = scalar_file_content
            if keep_formatting:
                scalar_node = FoldedScalarString(scalar_file_content)

            if scalar_file_name in data:
                raise DuplicateKey(
                    f"Duplicate key found inside {dir_path}: {yaml_file_name}"
                )

            data[scalar_file_name] = scalar_node

    # Recursively traverse directories.
    # Directory's name is considered to be the name of the nested field,
    # if it's not an array. Otherwise, directory name is ignored.
    for sub_dir in all_dirs:
        sub_dir_data = assemble_recursively(
            sub_dir,
            sort_paths=sort_paths,
            dry_run=dry_run,
            remove_comments=remove_comments,
            level=level + 1,
        )

        if sub_dir.name in data:
            raise DuplicateKey(
                f"Duplicate key found inside {dir_path}: {sub_dir.name}"
            )

        data[sub_dir.name] = sub_dir_data

    # Current directory is an array if either
    #   a. There is at least 1 item in it prefixed with a dash
    #   b. There is at least 1 grouper object that is a list
    is_current_dir_array = False
    for k, v in data.items():
        if k.startswith("-"):
            is_current_dir_array = True
            logger.debug((
                f"{indent}Level {dir_path} is an array because an item "
                f"with the dash prefix was found: {k}"
            ))
            break
        if k.startswith("+") and isinstance(v, list):
            is_current_dir_array = True
            logger.debug((
                f"{indent}Level {dir_path} is an array because a grouper "
                f"containing an array was found: {k}"
            ))
            break

    result_as_list: list = []
    result_as_dict: dict = {}
    for k, v in data.items():
        if k == "index" and isinstance(v, list):
            raise IndexFileIsArray((
                f"Directory {dir_path} contains an index file with an "
                "array."
            ))

        if is_current_dir_array:
            if k.startswith("-"):
                result_as_list.append(v)
            elif k.startswith("+") and isinstance(v, list):
                result_as_list.extend(v)
            else:
                # If current dir is an array, then all items in it
                # must be valid array items too.
                plain = k.lstrip("-+")
                raise InvalidItemWithinArrayDirectoryError((
                    f"Directory {dir_path} is an array, but it contains an "
                    f"unexpected value in key {k} (type: {type(v)}). Inside array folders, "
                    f"either the key should start with a dash -{plain} or "
                    f"the key must be a grouper +{plain} that contains "
                    f"another array within itself."
                ))
            
        else:
            if (k.startswith("+") or k == "index") and isinstance(v, dict):
                result_as_dict.update(v)
            else:
                result_as_dict[k] = v

    result = result_as_list if is_current_dir_array else result_as_dict
    logger.debug(f"{indent}Level {dir_path} returned {type(result)}")
    return result
