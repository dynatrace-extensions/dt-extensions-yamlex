import json
import logging
from pathlib import Path
from typing import Optional

import ruamel.yaml
import typer
from typing_extensions import Annotated

from yamlex.api.differ import diff as diff_data
from yamlex.api.util import adjust_root_logger
from yamlex.cli.common_flags import (
    verbose_flag,
    quiet_flag,
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
) -> None:
    """
    Compare --source YAML file or directory to --target and print the differences.

    Recursively compares the --source and --target YAML files or directories and
    prints the differences in JSON format. Diff does not care about the
    formatting of the --source and --target, only about the actual content.

    The data from --source will be marked as "old" in the diff and the data
    from --target will be marked as "new".

    Both --source and --target can be a file or a directory.

    Exits with exit code 0 if there is no difference. Otherwise, the exit
    code is 1.
    """
    adjust_root_logger(verbose, quiet)

    logger.debug(f"Source path: {source}")
    logger.debug(f"Target path: {target}")

    # Compare source to target
    difference = diff_data(
        source=source,
        target=target,
    )

    serialized = json.dumps(
        difference,
        indent=2,
        default=str,
    )
    print(serialized)

    if difference:
        raise typer.Exit(1)
