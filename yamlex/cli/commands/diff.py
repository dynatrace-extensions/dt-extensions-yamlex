import json
import logging
from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

from yamlex.api.differ import diff as diff_files
from yamlex.api.util import (
    adjust_root_logger,
)
from yamlex.cli.common_flags import (
    verbose_flag,
    quiet_flag,
    debug_flag,
)


logger = logging.getLogger(__name__)


def diff(
    source: Annotated[
        Optional[Path],
        typer.Option(
            "--source",
            "-s",
            help="Path to the source YAML file.",
            show_default=False,
            dir_okay=False,
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
            help="Path to the target extension.yaml.",
            show_default=False,
            dir_okay=False,
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
    Compare source YAML file to target and print the differences.
    """
    adjust_root_logger(verbose, quiet)

    logger.debug(f"Source file: {source}")
    logger.debug(f"Target file: {target}")

    # Load source and target files
    difference = diff_files(
        source_file_path=source,
        target_file_path=target,
        debug=debug,
    )

    serialized = json.dumps(
        difference,
        indent=2,
        default=str,
    )
    print(serialized)
