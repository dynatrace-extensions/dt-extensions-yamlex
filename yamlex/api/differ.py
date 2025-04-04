import logging
from pathlib import Path
from typing import Any

import ruamel.yaml
import ruamel.yaml.comments
from deepdiff import DeepDiff


logger = logging.getLogger(__name__)
parser = ruamel.yaml.YAML()


def diff(
    source_file_path: Path,
    target_file_path: Path,
    debug: bool = False,
) -> dict:
    """
    Compare two YAML files recursively and return the differences.

    Args:
        source_file_path (Path): Path to the source YAML file.
        target_file_path (Path): Path to the target YAML file.
        debug (bool): If True, print debug information.

    Returns:
        dict: A dictionary containing the differences between the two files.
    """
    # Load data from the source and target files
    with open(source_file_path, "r") as source_file:
        source_data: dict = parser.load(source_file)
    
    with open(target_file_path, "r") as target_file:
        target_data: dict = parser.load(target_file)

    differences = DeepDiff(
        source_data,
        target_data,
        ignore_order=True,
        report_repetition=True,
        verbose_level=2,
        # ignore_type_in_groups=[
        #     (ruamel.yaml.comments.CommentedSeq, ruamel.yaml.comments.CommentedMap),
        # ],
        # ignore_type_subclasses=True,
    )

    return differences


def list_item_key(item: Any) -> Any:
    """
    Generate a key for sorting list items.

    Args:
        item (Any): The item to generate a key for.

    Returns:
        Any: The key for the item.
    """
    if isinstance(item, dict):
        keys = item.keys()
        if "id" in item:
            return item["id"]
        if "idPattern" in item:
            return item["idPattern"]
        if "key" in item:
            return item["key"]
        if "path" in item:
            return item["path"]
        if "name" in item:
            return item["name"]
    return item

def compare(source: dict, target: dict) -> dict:
    """
    Compare source to target and return the differences.

    Args:
        source (Any): The source value.
        target (Any): The target value.

    Returns:
        dict: A dictionary containing the differences between two values.
    """
    differences = {}

    if isinstance(source, dict) and isinstance(target, dict):
        for key in source.keys():
            if key not in target:
                differences[key] = {"status": "removed", "value": source[key]}

            elif source[key] != target[key]:
                nested_diff = compare(source[key], target[key])
                if nested_diff:
                    differences[key] = {"status": "nested", "value": nested_diff}

        for key in target.keys():
            if key not in source:
                differences[key] = {"status": "added", "value": target[key]}

    elif isinstance(source, list) and isinstance(target, list):
        # Sort both lists to ensure order doesn't affect comparison
        sorted_source = sorted(source)
        sorted_target = sorted(target)

        # Find elements not present in target
        for item in sorted_source:
            if item not in sorted_target:
                differences[item] = {"status": "removed", "value": item}

        # Find elements not present in source
        for item in sorted_target:
            if item not in sorted_source:
                differences[item] = {"status": "added", "value": item}
    
    else:
        # Handle scalar values
        differences = {
            "status": "changed",
            "source": source,
            "target": target,
        }
    
    return differences