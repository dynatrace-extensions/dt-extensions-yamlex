import logging
from pathlib import Path

import ruamel.yaml
from deepdiff import DeepDiff

from yamlex.api.joiner import assemble_recursively
from yamlex.api.util import remove_yaml_comments
from yamlex.api.exceptions import (
    FailedToParseYamlError,
    InvalidPath,
)


logger = logging.getLogger(__name__)
parser = ruamel.yaml.YAML()


def diff(
    source: Path,
    target: Path,
) -> dict:
    """
    Compare two YAML files recursively and return the differences.

    Returns:
        dict: A dictionary containing the differences between the two files.
    """
    source_data = parse_path(source)
    target_data = parse_path(target)

    differences = DeepDiff(
        source_data,
        target_data,
        ignore_order=True,
        report_repetition=True,
        verbose_level=2,
    )

    return differences


def parse_path(path: Path) -> dict:
    if path.is_file(): 
        try:
            with open(path, "r") as file:
                raw_data: dict = parser.load(file)
        except Exception as e:
            raise FailedToParseYamlError(
                f"Failed to parse YAML in {path}: {e}"
            )
        data = remove_yaml_comments(
            path,
            raw_data,
            recursive=True,
        )
    elif path.is_dir():
        data = assemble_recursively(
            path,
            remove_comments=True,
        )
    else:
        raise InvalidPath(
            f"{path} must be a directory or a file."
        )
    return data
