import logging
from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

from yamlex.schema_mapper import update_vscode_settings_json
from yamlex.folder_structure import ensure_folder_structure
from yamlex.splitter import split_yaml
from yamlex.joiner import join_yaml


logging.basicConfig(level=logging.INFO, format="%(message)s")

logger = logging.getLogger(__name__)
app = typer.Typer(
    name="yamlex",
    rich_markup_mode="rich",
)

yaml_option = Annotated[
    Optional[Path],
    typer.Option(
        "--yaml",
        "-y",
        help=(
            "The directory containing the YAML files. "
            "Defaults to: 'src/extension/' or 'extension/'"
        ),
        show_default=False,
    ),
]
json_option = Annotated[
    Path,
    typer.Option(
        "--json",
        "-j",
        help="Path to the directory with JSON schema files.",
        exists=True,
        readable=True,
    ),
]
settings_option = Annotated[
    Path,
    typer.Option(
        "--settings",
        "-s",
        help="Path to the VS Code settings.json file.",
    ),
]
output_option = Annotated[
    Optional[Path],
    typer.Option(
        "--output",
        "-o",
        help="Path to output extension.yaml file.",
        show_default=False,
    ),
]
force_option = Annotated[
    bool,
    typer.Option(
        "--force",
        "-f",
        help="Overwrite the destination file if it was created manually.",
    ),
]
cwd_option = Annotated[
    Optional[Path],
    typer.Option(
        "--cwd",
        help="The current working directory to use.",
        exists=True,
        readable=True,
        hidden=True,
    ),
]
verbose_option = Annotated[
    bool,
    typer.Option(
        "--verbose",
        "-v",
        help="Enable verbose output.",
    ),
]
quiet_option = Annotated[
    bool,
    typer.Option(
        "--quiet",
        "-q",
        help="Disable any informational output. Only errors.",
    ),
]


def adjust_logging(verbose: bool = False, quiet: bool = False) -> None:
    if quiet:
        logging.root.setLevel(logging.ERROR)
    elif verbose:
        logging.root.setLevel(logging.DEBUG)


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
    logger.error("No extension directory found")
    exit(1)


@app.command(
    help=(
        "Enable VS Code to validate YAML schema of individual parts "
        "by mapping each of them to proper JSON schema in local "
        "VS Code settings file."
    ),
    name="map",
)
def map_(
    json: json_option = Path("schema"),
    settings: settings_option = Path(".vscode/settings.json"),
    yaml: yaml_option = None,
    cwd: cwd_option = Path("."),
    verbose: verbose_option = False,
    quiet: quiet_option = False,
):
    """Map YAML files to JSON schema."""
    adjust_logging(verbose, quiet)

    logger.info("Mapping YAML files to JSON schema...")
    logger.debug(f"Current working directory: {cwd}")

    json_schemas_dir_path = json
    if not json_schemas_dir_path.is_absolute():
        json_schemas_dir_path = cwd / json_schemas_dir_path
    logger.debug(f"JSON schema files directory: {json}")

    vscode_settings_json_file_path = settings
    if not vscode_settings_json_file_path.is_absolute():
        vscode_settings_json_file_path = cwd / vscode_settings_json_file_path
    logger.debug(f"VS Code settings.json file: {settings}")

    extension_yaml_dir_path = yaml or get_default_extension_dir_path()
    if not extension_yaml_dir_path.is_absolute():
        extension_yaml_dir_path = cwd / extension_yaml_dir_path
    logger.debug(f"Extension YAML files directory: {yaml}")

    update_vscode_settings_json(
        json_schemas_dir_path,
        vscode_settings_json_file_path,
        extension_yaml_dir_path,
    )


@app.command(help="Ensure the folder structure to store YAML files is in place.")
def structure(
    datasource_name: Annotated[str, typer.Argument(..., help="The name of the datasource.")],
    yaml: yaml_option = None,
    cwd: cwd_option = Path("."),
    verbose: verbose_option = False,
    quiet: quiet_option = False,
):
    """Ensure the folder structure is in place."""
    adjust_logging(verbose, quiet)

    logger.info("Ensuring the folder structure is in place...")

    extension_yaml_dir_path = yaml or get_default_extension_dir_path()
    if not extension_yaml_dir_path.is_absolute():
        extension_yaml_dir_path = cwd / extension_yaml_dir_path
    logger.debug(f"Extension YAML files directory: {extension_yaml_dir_path}")

    ensure_folder_structure(extension_yaml_dir_path, datasource_name)


@app.command(help="Split central YAML file into parts.")
def split(
    yaml: yaml_option = None,
    cwd: cwd_option = Path("."),
    verbose: verbose_option = False,
    quiet: quiet_option = False,
):
    """Decompose the central YAML file into parts."""
    adjust_logging(verbose, quiet)

    logger.info("Decomposing the central YAML file into parts...")

    extension_yaml_dir_path = yaml or get_default_extension_dir_path()
    if not extension_yaml_dir_path.is_absolute():
        extension_yaml_dir_path = cwd / extension_yaml_dir_path
    logger.debug(f"Extension YAML files directory: {yaml}")

    split_yaml(extension_yaml_dir_path)


@app.command(help="Join YAML files into a single file.")
def join(
    yaml: yaml_option = None,
    output: output_option = None,
    force: force_option = False,
    cwd: cwd_option = Path("."),
    verbose: verbose_option = False,
    quiet: quiet_option = False,
):
    """Run the application."""
    adjust_logging(verbose, quiet)

    extension_yaml_dir_path = yaml or get_default_extension_dir_path()
    if not extension_yaml_dir_path.is_absolute():
        extension_yaml_dir_path = cwd / extension_yaml_dir_path
    logger.debug(f"Extension YAML files directory: {yaml}")

    output_file_path = output or extension_yaml_dir_path / "extension.yaml"
    if not output_file_path.is_absolute():
        output_file_path = cwd / output_file_path
    logger.debug(f"Output file: {output}")

    join_yaml(extension_yaml_dir_path, output_file_path, force)
