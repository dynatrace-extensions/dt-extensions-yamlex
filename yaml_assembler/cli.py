import logging
from pathlib import Path

import typer
# from rich.console import Console
from typing_extensions import Annotated

from yaml_assembler import __version__
from yaml_assembler.schema_mapper import update_vscode_settings_json
from yaml_assembler.folder_structure import ensure_folder_structure
from yaml_assembler.disassembler import disassemble_yaml
from yaml_assembler.assembler import assemble_yaml


# Basic configuration for logging
logging.basicConfig(
    level=logging.DEBUG,
    # format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    format="%(levelname)s | %(message)s",
)

app = typer.Typer()
# console = Console()
logger = logging.getLogger(__name__)


@app.command()
def version():
    """Show the version of the application."""
    print(f"assemble-yaml version: {__version__}")


@app.command(
    help="Map YAML files to JSON schema for extension in .vscode/settings.json.",
    name="map",
)
def map_(
    json: Annotated[
        Path,
        typer.Option(
            "--json",
            "-j",
            help="Path to the directory with JSON schema files.",
            exists=True,
            readable=True,
        )
    ] = Path("schema"),
    settings: Annotated[
        Path,
        typer.Option(
            "--settings",
            "-s",
            help="Path to the VS Code settings.json file.",
        )
    ] = Path(".vscode/settings.json"),
    yaml: Annotated[
        Path,
        typer.Option(
            "--yaml",
            "-y",
            help="The directory containing the YAML files to be mapped.",
            exists=True,
            readable=True,
        )
    ] = Path("extension"),
    cwd: Annotated[
        Path,
        typer.Option(
            "--cwd",
            help="The current working directory to use.",
            exists=True,
            readable=True,
            hidden=True,
        )
    ] = Path("."),
):
    """Map YAML files to JSON schema."""
    logger.info("Mapping YAML files to JSON schema...")
    logger.info(f"Current working directory: {cwd}")

    json_schemas_dir_path = json
    if not json_schemas_dir_path.is_absolute():
        json_schemas_dir_path = cwd / json_schemas_dir_path
    logger.info(f"JSON schema files directory: {json}")

    vscode_settings_json_file_path = settings
    if not vscode_settings_json_file_path.is_absolute():
        vscode_settings_json_file_path = cwd / vscode_settings_json_file_path
    logger.info(f"VS Code settings.json file: {settings}")

    extension_yaml_dir_path = yaml
    if not extension_yaml_dir_path.is_absolute():
        extension_yaml_dir_path = cwd / extension_yaml_dir_path
    logger.info(f"Extension YAML files directory: {yaml}")

    update_vscode_settings_json(
        json_schemas_dir_path,
        vscode_settings_json_file_path,
        extension_yaml_dir_path,
    )


@app.command(help="Ensure the folder structure to store YAML files is in place.")
def structure(
    datasource_name: Annotated[str, typer.Argument(..., help="The name of the datasource.")],
    yaml: Annotated[Path, typer.Option("--yaml", "-y")] = Path("extension"),
    cwd: Annotated[
        Path,
        typer.Option(
            "--cwd",
            help="The current working directory to use.",
            exists=True,
            readable=True,
            hidden=True,
        )
    ] = Path("."),
):
    """Ensure the folder structure is in place."""
    logger.info("Ensuring the folder structure is in place...")

    extension_yaml_dir_path = yaml
    if not extension_yaml_dir_path.is_absolute():
        extension_yaml_dir_path = cwd / extension_yaml_dir_path
    logger.info(f"Extension YAML files directory: {extension_yaml_dir_path}")

    ensure_folder_structure(extension_yaml_dir_path, datasource_name)


@app.command(help="Split central YAML file into parts.")
def disassemble(
    yaml: Annotated[
        Path,
        typer.Option(
            "--yaml",
            "-y",
            help="The directory containing the YAML files.",
            exists=True,
            readable=True,
        )
    ] = Path("extension"),
    cwd: Annotated[
        Path,
        typer.Option(
            "--cwd",
            help="The current working directory to use.",
            exists=True,
            readable=True,
            hidden=True,
        )
    ] = Path("."),
):
    """Decompose the central YAML file into parts."""
    logger.info("Decomposing the central YAML file into parts...")

    extension_yaml_dir_path = yaml
    if not extension_yaml_dir_path.is_absolute():
        extension_yaml_dir_path = cwd / extension_yaml_dir_path
    logger.info(f"Extension YAML files directory: {yaml}")

    disassemble_yaml(extension_yaml_dir_path)


@app.command(help="Assemble YAML files into a single file.")
def assemble(
    yaml: Annotated[
        Path,
        typer.Option(
            "--yaml",
            "-y",
            help="The directory containing the YAML files to be assembled.",
        )
    ] = Path("extension"),
    output: Annotated[
        Path,
        typer.Option(
            "--output",
            "-o",
            help="Path to output extension.yaml file.",
        )
    ] = Path("extension/extension.yaml"),
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            help="Overwrite the destination file if it was created manually.",
        )
    ] = False,
    cwd: Annotated[
        Path,
        typer.Option(
            "--cwd",
            help="The current working directory to use.",
            exists=True,
            readable=True,
            hidden=True,
        )
    ] = Path("."),
):
    """Run the application."""
    logger.info("YAML files... assemble! (epic music starts playing)")

    extension_yaml_dir_path = yaml
    if not extension_yaml_dir_path.is_absolute():
        extension_yaml_dir_path = cwd / extension_yaml_dir_path
    logger.info(f"Extension YAML files directory: {yaml}")

    output_file_path = output
    if not output_file_path.is_absolute():
        output_file_path = cwd / output_file_path
    logger.info(f"Output file: {output}")

    assemble_yaml(extension_yaml_dir_path, output_file_path, force)
