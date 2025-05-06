import logging
from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

from yamlex.api.joiner import (
    assemble_recursively,
    remove_yaml_comments,
)
from yamlex.api.util import (
    adjust_root_logger,
    get_default_extension_dir_path,
    get_default_extension_source_dir_path,
    is_manually_created,
    write_file,
    read_version_properties,
    parse_version,
)
from yamlex.cli.common_flags import (
    no_comment_flag,
    force_flag,
    verbose_flag,
    quiet_flag,
    debug_flag,
)


logger = logging.getLogger(__name__)


def join(
    source: Annotated[
        Optional[Path],
        typer.Option(
            "--source",
            "-s",
            help="Path to the directory where individual source component files are stored.",
            show_default="source or src/source",
            dir_okay=True,
            file_okay=False,
            exists=True,
            readable=True,
        )
    ] = None,
    target: Annotated[
        Optional[Path],
        typer.Option(
            "--target",
            "-t",
            help="Path to the target extension.yaml file that will be assembled from parts.",
            show_default="extension/extension.yaml or src/extension/extension.yaml",
            dir_okay=False,
            file_okay=True,
        )
    ] = None,
    dev: Annotated[
        bool,
        typer.Option(
            "--dev",
            "-d",
            help="Add 'custom:' prefix and explicit version when producing extension.yaml.",
        ),
    ] = False,
    keep_formating: Annotated[
        bool,
        typer.Option(
            "--keep",
            "-k",
            help="Keep formatting and indentation when adding non-yaml files into extension.yaml.",
        ),
    ] = True,
    version: Annotated[
        Optional[str],
        typer.Option(
            "--version",
            "-v",
            help="Explicitly set the version in the extension.yaml.",
            show_default=False,
        ),
    ] = None,
    line_length: Annotated[
        Optional[int],
        typer.Option(
            "--line-length",
            help="Maximum line length in the generated extension.yaml.",
            show_default="not limited",
        ),
    ] = None,
    sort_paths: Annotated[
        bool,
        typer.Option(
            "--sort-paths",
            help="Sort paths alphabetically when traversing source directory before join.",
        ),
    ] = False,
    no_comment: no_comment_flag = False,
    force: force_flag = False,
    verbose: verbose_flag = False,
    quiet: quiet_flag = False,
    debug: debug_flag = False,
) -> None:
    """
    Join individual components into a single [i]extension.yaml[/i] file.

    Assembles all files from the --source directory in a hierarchical order.
    As if the folder structure of the source directory represents a YAML
    structure.

    [b]How it works[/b]

    - Any folder or file within the --source directory is considered to be
      a field within the final extension.yaml. For example, a file called
      [i]name.yaml[/i] will become a field called [i]name:[/i] and its content will be
      put into that field.

    - Nesting level of the included file or folder matches its
      indentation level within the resulting file.

    - If a folder contains a special file called [i]index.yaml[/i], then the
      content of that file is added on the same level as the folder. For
      example, 

    - If any of the items within the folder start with the minus sign "-" in
      their name, then the whole folder is considered to be an array.

    - If a folder name starts with a plus sign "+", then the folder is
      considered to be a grouper folder and yamlex behaves as if that folder
      does not add any additional level of nesting at all.

    - If a folder or a file starts with the exclamation mark symbol "!", then
      it will be ignored, as if it doesn't exist at all.

    [b]Full example:[/b]

    [i]Source folder structure:[/i]          [i]Content of files on the left:[/i]

    source:
    ├── metadata.yaml                 name: My name is yamlex
    ├── folder
    │   ├── query.sql                 SELECT * FROM DUAL
    │   ├── !some.yaml                text: This file will be skipped
    │   └── index.yaml                group: My Query
    ├── +grouper
    │   └── normal.yaml               present: value
    └── array
        ├── -item_1.yaml              call: fus
        ├── -item_2.yaml              call: roh
        └── -item_3
             └── index.yaml           call: dah

    [i]Resulting extension.yaml:[/i]

    metadata:
      name: My name is yamlex
    folder:
      group: My Query
      query: SELECT * FROM DUAL
    present: value
    array:
      - call: fus
      - call: roh
      - call: dah

    [b]Overwriting existing extension.yaml (--no-comment and --force)[/b]

    Yamlex tries to be cautious not to accidentally overwrite a manually
    created [i]extension.yaml[/i]. If that file contains the "Generated with
    yamlex" line in it, then yamlex overwrites it without hesitation.
    However, when [i]extension.yaml[/i] does not contain that line, yamlex
    does not overwrite it. You can alter this behaviour using --force flag.
    
    When yamlex generates the [i]extension.yaml[/i] from parts, it adds the
    same comment at the top: # Generated by yamlex
    If you would like to disable this behaviour, use the --no-comment flag.

    [b]Development mode[/b]

    When you add the --dev flag, yamlex will add the "custom:" prefix to the
    name of your extension and will put an explicit version into the final
    [i]extension.yaml[/i].
    """
    adjust_root_logger(verbose, quiet)

    source = source or get_default_extension_source_dir_path()
    logger.debug(f"Source files directory: {source}")

    try:
        extension = assemble_recursively(
            source,
            non_yaml_files_as_scalars=keep_formating,
            debug=debug,
            sort_paths=sort_paths,
        )
    except UnicodeDecodeError as e:
        # If any non-text files were caught up in the processing because they
        # happened to be placed into the source directory, we can catch it
        # here, since these files would file to be decoded as utf-8.
        logger.error(f"Found non-text file in the source directory: {e}")
        raise typer.Exit(1)

    # Figure out the current version
    yaml_version = extension.get("version")

    if dev:
        name = extension.get("name")
        if isinstance(name, str) and not name.startswith("custom:"):
            name = f"custom:{name}"
            extension["name"] = name
            logger.info(f"Dev mode extension name: {name}")

        # If new version is not explicitly specified
        if not version:
            current_version = parse_version(yaml_version)
            if not current_version:
                current_version = read_version_properties("version.properties")
                logger.info(f"Version found in version.properties: {current_version}")

        # Update version, if new explicit version was specified
        if not version:
            version = current_version

        # Explicitly add version to generated extension.yaml
        if yaml_version != version:
            extension["version"] = version
            logger.info(f"Explicit version in dev mode: {version}")

    target = target or get_default_extension_dir_path() / "extension.yaml"
    logger.debug(f"Target file: {target}")

    # Check if the target file exists and was created manually
    if is_manually_created(target) and not force:
        logger.error(f"The {target} file was created manually. Use --force to overwrite it.")
        exit(2)

    # Remove comments
    remove_yaml_comments(extension)

    # Write to output file
    should_add_comment = not no_comment
    write_file(
        target,
        extension,
        add_comment=should_add_comment,
        line_length=line_length,
    )

    if debug:
        print(extension)
