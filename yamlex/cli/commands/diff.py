import json
import logging
from pathlib import Path
from typing import Optional

import ruamel.yaml
import typer
from typing_extensions import Annotated

from yamlex.api.differ import diff as diff_data
from yamlex.api.joiner import assemble_recursively
from yamlex.api.util import (
    adjust_root_logger,
)
from yamlex.cli.common_flags import (
    verbose_flag,
    quiet_flag,
    debug_flag,
)
from yamlex.api.exceptions import (
    FailedToParseYamlError,
    InvalidSourcePath,
    InvalidTargetPath,
)


logger = logging.getLogger(__name__)
parser = ruamel.yaml.YAML()


def diff(
    source: Annotated[
        Optional[Path],
        typer.Option(
            "--source",
            "-s",
            help="Path to the source directory or YAML file.",
            show_default=False,
            dir_okay=True,
            file_okay=True,
            exists=True,
            readable=True,
        )
    ] = None,
    target: Annotated[
        Optional[Path],
        typer.Option(
            "--target",
            "-t",
            help="Path to the target directory or YAML file.",
            show_default=False,
            dir_okay=True,
            file_okay=True,
            exists=True,
            readable=True,
        )
    ] = None,
    verbose: verbose_flag = False,
    quiet: quiet_flag = False,
    debug: debug_flag = False,
) -> None:
    """
    Compare source YAML file or directory to target and print the differences.

    Recursively compares the source and target YAML files or directories and
    prints the differences in JSON format. Diff does not care about the
    formatting of the source and target, only about the actual content.

    Both source and target can be a file or a directory.

    Exits with exit code 0 if there is no difference. Otherwise, the exit
    code is 1.
    """
    adjust_root_logger(verbose, quiet)

    logger.debug(f"Source path: {source}")
    logger.debug(f"Target path: {target}")

    if source.is_file():
        try:
            with open(source, "r") as source_file:
                source_data: dict = parser.load(source_file)
        except Exception as se:
            raise FailedToParseYamlError(
                f"Failed to parse YAML in {source}: {se}"
            )
    elif source.is_dir():
        source_data = assemble_recursively(
            source,
            debug=debug,
            remove_comments=True,
        )
    else:
        raise InvalidSourcePath(
            f"Source {source} must be a directory or a file."
        )

    if target.is_file(): 
        try:
            with open(target, "r") as target_file:
                target_data: dict = parser.load(target_file)
        except Exception as te:
            raise FailedToParseYamlError(
                f"Failed to parse YAML in {target}: {te}"
            )
    elif target.is_dir():
        target_data = assemble_recursively(
            target,
            debug=debug,
            remove_comments=True,
        )
    else:
        raise InvalidTargetPath(
            f"Target {target} must be a directory or a file."
        )

    # Compare source to target
    difference = diff_data(
        source_data=source_data,
        target_data=target_data,
        debug=debug,
    )

    serialized = json.dumps(
        difference,
        indent=2,
        default=str,
    )
    print(serialized)

    if difference:
        raise typer.Exit(1)
