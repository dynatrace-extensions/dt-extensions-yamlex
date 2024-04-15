import json
import logging
from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

from yamlex.api.mapper import (
    validate_json_schemas_dir,
    map_schema_to_sources,
    read_vscode_settings_json_file,
    extract_definitions_into_standalone_schemas,
)
from yamlex.api.util import (
    adjust_root_logger,
    get_default_extension_dir_path,
    get_default_extension_source_dir_path,
)

from yamlex.cli.common_flags import (
    verbose_flag,
    quiet_flag,
)


logger = logging.getLogger(__name__)


def map(
    settings: Annotated[
        Path,
        typer.Argument(
            help="Path to the VS Code settings.json file.",
        ),
    ] = Path(".vscode/settings.json"),
    schema: Annotated[
        Path,
        typer.Option(
            "--json",
            "-j",
            help="Path to directory with valid extensions JSON schema files.",
            exists=True,
            readable=True,
            dir_okay=True,
            file_okay=False,
        ),
    ] = Path("schema"),
    source: Annotated[
        Optional[Path],
        typer.Option(
            "--source",
            "-s",
            help="Path to directory where YAML source files will be stored.",
            show_default="[default: source or src/source]",
            dir_okay=True,
            file_okay=False,
        )
    ] = None,
    root: Annotated[
        Path,
        typer.Option(
            "--root",
            "-r",
            help="Root directory relative to which the paths in settings file will be mapped.",
            dir_okay=True,
            file_okay=False,
        )
    ] = Path("."),
    extension_yaml: Annotated[
        Optional[Path],
        typer.Option(
            "--extension-yaml",
            "-e",
            help="Path to output extension.yaml file.",
            show_default="[default: extension/extension.yaml or src/extension/extension.yaml]",
            dir_okay=False,
            file_okay=True,
        )
    ] = None,
    verbose: verbose_flag = False,
    quiet: quiet_flag = False,
) -> None:
    """
    Map JSON schema to YAML files in VS Code settings.
    """
    adjust_root_logger(verbose, quiet)
    logger.debug(f"JSON schema files directory: {schema}")
    logger.debug(f"VS Code settings.json file: {settings}")
    logger.debug(f"Root dir: {root}")

    source = source or get_default_extension_source_dir_path()
    logger.debug(f"Extension YAML source files directory: {source}")

    extension_yaml = extension_yaml or get_default_extension_dir_path() / "extension.yaml"
    logger.debug(f"extension.yaml file: {extension_yaml}")

    # Make sure schemas directory contains extension.schema.json
    validate_json_schemas_dir(schema)

    # Make schema more granular by extracting embedded definitions into
    # separate schema files.
    extract_definitions_into_standalone_schemas(schema)

    # Update yaml.schemas mapping in settings.json
    vscode_settings = read_vscode_settings_json_file(settings)

    # Delete existing extension.yaml mapping
    mapping: dict = vscode_settings.get("yaml.schemas", {})
    for k, v in mapping.items():
        if "extension.yaml" in str(v):
            del mapping[k]
            break
    
    # Update the mapping
    mapping_update = map_schema_to_sources(schema, source, root, extension_yaml)
    mapping.update(mapping_update)

    # Write the updated settings.json file
    vscode_settings["yaml.schemas"] = mapping
    with open(settings, "w") as f:
        vscode_settings_file_text = json.dumps(vscode_settings, indent=2)
        f.write(vscode_settings_file_text)
        logger.info(f"Updated {settings} with new YAML schema mappings.")