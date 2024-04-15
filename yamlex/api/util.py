import logging
import re
from io import StringIO
from pathlib import Path
from typing import Optional, Union

import ruamel.yaml


logger = logging.getLogger(__name__)
parser = ruamel.yaml.YAML()


def adjust_root_logger(verbose: bool = False, quiet: bool = False) -> None:
    if quiet:
        logging.root.setLevel(logging.ERROR)
    elif verbose:
        logging.root.setLevel(logging.DEBUG)


def get_default_extension_source_dir_path() -> Path:
    src_dir_path = Path("src")
    if src_dir_path.exists() and src_dir_path.is_dir():
        return src_dir_path / "source"
    else:
        return Path("source")


def get_default_extension_dir_path() -> Path:
    candidates = [
        Path("extension"),
        Path("src/extension"),
    ]

    # Find the first suitable candidate
    for candidate in candidates:
        # Check the candidate directory exists
        if candidate.exists() and candidate.is_dir():
            return candidate
        continue

    # Nothing suitable was found
    logger.error(
        (
            "No default extension directory found. "
            "'extension/' or 'src/extension/' folder must exist "
            "in the current working directory."
        )
    )
    exit(1)


def is_manually_created(path: Path) -> bool:
    if path.exists():
        with open(path, "r") as f:
            content = f.read().lower()
            if "generated by yamlex" not in content:
                True
    return False


def write_file(
    file_path: Path,
    data: Union[dict, list],
    add_comment: bool = True,
) -> None:
    # Convert dict to YAML. Dump to string first to add a comment
    stream = StringIO()
    parser.indent(mapping=2, sequence=4, offset=2)
    parser.dump(data, stream)
    text = stream.getvalue()

    # Make sure the directory we write to exists
    dir = file_path.parent.resolve()
    dir.mkdir(parents=True, exist_ok=True)

    # Write to output file
    with open(file_path, "w") as f:
        if add_comment:
            # Write a comment to indicate that the file was automatically generated
            comment = f"# Generated by yamlex\n\n"
            f.write(comment)
        f.write(text)


def read_version_properties(path: Path, default: Optional[str] = None) -> str:
    try:
        with open(path, "r") as f:
            content = f.read()
            match_ = re.search(r"version=(.*)", content)
            if not match_ and not default:
                raise KeyError("Could not read current version")
            return match_.group(1)
    except Exception as e:
        logger.error(f"Failed to open {path}: {e}")
        exit(1)


def write_version_properties(path: Path, version: str) -> None:
    try:
        with open(path, "r") as rf:
            lines = rf.readlines()
            content = []
            for l in lines:
                if l.startswith("version"):
                    content.append(f"version={version}\n")
                else:
                    content.append(l)
        with open(path, "w") as wf:
            wf.writelines(content) 
    except Exception as e:
        logger.error(f"Failed to write to {path}: {e}")
        exit(1)


def parse_version(version: str) -> Optional[str]:
    regex = r"^(0|[1-9][0-9]{0,3})(\.(0|[1-9][0-9]{0,3})){0,2}$"
    match_ = re.search(regex, version)
    if not match_:
        return None
    return match_.group()


def bump_version(version: str) -> str:
    version_parts = version.split(".")
    part_int: int | None = None
    part_idx: int | None = None
    for i, part in enumerate(reversed(version_parts)):
        try:
            part_int = int(part)
            part_idx = len(version_parts) - 1 - i
            break
        except:
            continue
    if part_int is None:
        logger.error("Could not find integer part in version")
        exit(1)

    part_int += 1
    result = ""
    for i, part in enumerate(version_parts):
        append = part
        if i == part_idx:
            append = part_int
        result += f"{append}."
    result = result.rstrip(".")
    return result