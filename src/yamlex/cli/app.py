import logging
import sys
from typing import Optional
from typing_extensions import Annotated

import typer
from rich import print

from yamlex.cli.commands.join import join as join_cmd
from yamlex.cli.commands.map import map as map_cmd
from yamlex.cli.commands.split import split as split_cmd
from yamlex.cli.commands.diff import diff as diff_cmd
from yamlex.cli.version import get_version
from yamlex.api.exceptions import (
    YamlexError,
)


logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


help_text = """
[b]How assembling works:[/b]

- [b]Hierarchy preserved[/b]
  
  Any folder or file within the --source directory is considered to be
  a field within the final extension.yaml. For example, a file called
  [i]name.yaml[/i] will become a field called [i]name:[/i] and its content
  will be put into that field.

  [i]Example 1[/i]:
  ┌───────────────────────────────────┬───────────────────────────────────┐
  │ [i]Source folder structure:[/i]          │ [i]Contents of the file:[/i]             │
  │ source/                           │                                   │
  │ └── author.yaml                   │ name: John Doe                    │
  ├───────────────────────────────────┼───────────────────────────────────┤
  │ [i]Resulting extension.yaml:[/i]         │                                   │
  │ author:                           │                                   │
  │   name: John Doe                  │                                   │
  └───────────────────────────────────┴───────────────────────────────────┘
    
- [b]Arrays with '-' symbol[/b]

  The minus sign '-' in front of a file or directory inside a parent
  folder means that the parent folder is an array. Every item within
  that folder will become an array item and the folder itself will
  be added as an array to the final yaml.

  [i]Example 2[/i]:

  ┌───────────────────────────────────┬───────────────────────────────────┐
  │ [i]Source folder structure:[/i]          │ [i]Contents of the file:[/i]             │
  │ source/                           │                                   │
  │ ├── metrics/                      │                                   │
  │ │   └── -metric_1.yaml            │ key: metric_1                     │
  │ └── +index.yaml                   │ name: com.example.extension.test  │
  ├───────────────────────────────────┼───────────────────────────────────┤
  │ [i]Resulting extension.yaml:[/i]         │                                   │
  │ name: com.example.extension.test  │                                   │
  │ metrics:                          │                                   │
  │   - key: metric_1                 │                                   │
  └───────────────────────────────────┴───────────────────────────────────┘

  [i]Example 3 (same result, using different structure)[/i]:

  ┌───────────────────────────────────┬───────────────────────────────────┐
  │ [i]Source folder structure:[/i]          │ [i]Contents of the file:[/i]             │
  │ source/                           │                                   │
  │ ├── metrics/                      │                                   │
  │ │   └── -metric_1/                │                                   │
  │ │       └── index.yaml            │ key: metric_1                     │
  │ └── +index.yaml                   │ name: com.example.extension.test  │
  ├───────────────────────────────────┼───────────────────────────────────┤
  │ [i]Resulting extension.yaml:[/i]         │                                   │
  │ name: com.example.extension.test  │                                   │
  │ metrics:                          │                                   │
  │   - key: metric_1                 │                                   │
  └───────────────────────────────────┴───────────────────────────────────┘

- [b]Groupers with '+' symbol[/b]

  If the name of a folder or file starts with a + symbol, then the
  content of that file or folder is added on the same level as the folder
  itself.

  The folder itself is ignored, but [i]everything[/i] inside it is used.
  With the + in front, the folder or file become a "virtual"
  hierarchy, which doesn't add a new nesting level in the final yaml.
  However, anything inside such folder or file will be added on the same
  level as the parent. Almost as if the +folder/ or +file.yaml do not
  exist at all and their content just gets added to the parent.

  [i]Example 4[/i]:

  ┌───────────────────────────────────┬───────────────────────────────────┐
  │ [i]Source folder structure:[/i]          │ [i]Contents of the file:[/i]             │
  │ source/                           │                                   │
  │ ├── author.yaml                   │ name: John Doe                    │
  │ └── +index.yaml                   │ name: com.example.extension.test  │
  │                                   │ minDynatraceVersion: 1.295.0      │
  ├───────────────────────────────────┼───────────────────────────────────┤
  │ [i]Resulting extension.yaml:[/i]         │                                   │
  │ name: com.example.extension.test  │                                   │
  │ minDynatraceVersion: 1.295.0      │                                   │
  │ author:                           │                                   │
  │   name: John Doe                  │                                   │
  └───────────────────────────────────┴───────────────────────────────────┘

  [i]Example 5[/i]:

  ┌───────────────────────────────────┬───────────────────────────────────┐
  │ [i]Source folder structure:[/i]          │ [i]Contents of the file:[/i]             │
  │ source/                           │                                   │
  │ ├── author.yaml                   │ name: John Doe                    │
  │ └── +grouper.yaml                 │ name: com.example.extension.test  │
  │                                   │ minDynatraceVersion: 1.295.0      │
  ├───────────────────────────────────┼───────────────────────────────────┤
  │ [i]Resulting extension.yaml:[/i]         │                                   │
  │ name: com.example.extension.test  │                                   │
  │ minDynatraceVersion: 1.295.0      │                                   │
  │ author:                           │                                   │
  │   name: John Doe                  │                                   │
  └───────────────────────────────────┴───────────────────────────────────┘

  [i]Example 6[/i]:

  ┌───────────────────────────────────┬───────────────────────────────────┐
  │ [i]Source folder structure:[/i]          │ [i]Contents of the file:[/i]             │
  │ source/                           │                                   │
  │ ├── metrics/                      │                                   │
  │ │   └── +group_of_metrics.yaml    │ - key: metric_1                   │
  │ └── +index.yaml                   │ name: com.example.extension.test  │
  ├───────────────────────────────────┼───────────────────────────────────┤
  │ [i]Resulting extension.yaml:[/i]         │                                   │
  │ name: com.example.extension.test  │                                   │
  │ metrics:                          │                                   │
  │   - key: metric_1                 │                                   │
  └───────────────────────────────────┴───────────────────────────────────┘

  [i]Example 7[/i]:

  ┌───────────────────────────────────┬───────────────────────────────────┐
  │ [i]Source folder structure:[/i]          │ [i]Contents of the file:[/i]             │
  │ source/                           │                                   │
  │ ├── metrics/                      │                                   │
  │ │   └── +group_of_metrics/        │                                   │
  │ │       └── -metric_1.yaml        │ key: metric_1                     │
  │ └── +index.yaml                   │ name: com.example.extension.test  │
  ├───────────────────────────────────┼───────────────────────────────────┤
  │ [i]Resulting extension.yaml:[/i]         │                                   │
  │ name: com.example.extension.test  │                                   │
  │ metrics:                          │                                   │
  │   - key: metric_1                 │                                   │
  └───────────────────────────────────┴───────────────────────────────────┘

- [b]Ignoring with '!' symbol[/b]

  If a folder or a file starts with the exclamation mark symbol '!', then
  it will be ignored, as if it doesn't exist at all, including all its
  content. This is useful for excluding files or folders from the final
  yaml.

  [i]Example 8[/i]:

  ┌───────────────────────────────────┬───────────────────────────────────┐
  │ [i]Source folder structure:[/i]          │ [i]Contents of the file:[/i]             │
  │ source/                           │                                   │
  │ ├── !metrics/                     │                                   │
  │ │   └── -metric_1.yaml            │ key: metric_1                     │
  │ └── +index.yaml                   │ name: com.example.extension.test  │
  ├───────────────────────────────────┼───────────────────────────────────┤
  │ [i]Resulting extension.yaml:[/i]         │                                   │
  │ name: com.example.extension.test  │                                   │
  └───────────────────────────────────┴───────────────────────────────────┘

- [b]Scalar files[/b]

  Any plain text file (not yaml) will be added as a scalar value. With
  the formatting preserved. 

  [i]Example 9[/i]:

  ┌───────────────────────────────────┬───────────────────────────────────┐
  │ [i]Source folder structure:[/i]          │ [i]Contents of the file:[/i]             │
  │ source/                           │                                   │
  │ └── vars/                         │                                   │
  │     └── -timeout/                 │                                   │
  │         ├── description.txt       │ Custom timeout.                   │
  │         └── +index.yaml           │ id: timeout                       │
  │                                   │ type: text                        │
  │                                   │ defaultValue: "120"               │
  ├───────────────────────────────────┼───────────────────────────────────┤
  │ [i]Resulting extension.yaml:[/i]         │                                   │
  │ vars:                             │                                   │
  │   - id: timeout                   │                                   │
  │     description: Custom timeout.  │                                   │
  │     type: text                    │                                   │
  │     defaultValue: "120"           │                                   │
  └───────────────────────────────────┴───────────────────────────────────┘
"""


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
        help=help_text,
        pretty_exceptions_enable=False,
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
    app.command(name="d", hidden=True)(diff_cmd)

    # Launch Typer app.
    try:
        app()
    except YamlexError as e:
        code = e.code
        name = e.__class__.__name__
        message = f" {e.args[0]}" if e.args else ""
        print(f"Error {code} ({name})!{message}", file=sys.stderr)
        exit(code)
