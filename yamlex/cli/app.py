import logging
from typing import Optional
from typing_extensions import Annotated

import typer
from rich import print

from yamlex.cli.commands.join import join as join_cmd
from yamlex.cli.commands.map import map as map_cmd
from yamlex.cli.commands.split import split as split_cmd
from yamlex.cli.commands.diff import diff as diff_cmd
from yamlex.cli.version import get_version


logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def callback(
    ctx: typer.Context,
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            "-v",
            show_default=False,
            is_eager=True,
        ),
    ] = None,
) -> None:
    if version:
        prog_version = get_version()
        print(prog_version)

        raise typer.Exit()
    
    if ctx.invoked_subcommand:
        return


def run() -> None:
    # Set up Typer app.
    app = typer.Typer(
        name="yamlex",
        rich_markup_mode="rich",
        add_completion=False,
        context_settings={"help_option_names": ["-h", "--help"]},
    )

    # Set primary callback. This shows helps or allows to show version.
    app.callback(invoke_without_command=True, no_args_is_help=True)(callback)

    # Declare main commands.
    app.command(name="map")(map_cmd)
    app.command(name="split")(split_cmd)
    app.command(name="join")(join_cmd)
    app.command(name="diff")(diff_cmd)

    # Declare aliases for popular commands.
    app.command(name="j", hidden=True)(join_cmd)
    app.command(name="s", hidden=True)(split_cmd)

    # Launch Typer app.
    app()
