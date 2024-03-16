import json
import logging
import re
from pathlib import Path


logger = logging.getLogger(__name__)


def update_vscode_settings_json(
    json_schemas_dir_path: Path,
    vscode_settings_json_file_path: Path,
    extension_yaml_dir_path: Path,
):
    """Map YAML files to JSON schema."""
    # Check that directory with Extension JSON schema files exists and are valid
    check_json_schemas_dir_exists(json_schemas_dir_path)

    # Check that directory with Extension YAML files exists
    check_extension_yaml_dir_exists(extension_yaml_dir_path)

    # Convert each definition from extension.schema.json to a separate schema file
    extract_definitions_into_standalone_schemas(json_schemas_dir_path)

    # Read settings.json if it exists, otherwise create an empty dictionary
    project_dir_path = vscode_settings_json_file_path.parent.parent
    vscode_settings = read_vscode_settings_json_file(vscode_settings_json_file_path)
    
    # Check if yaml.schemas mapping field exists in settings.json
    if "yaml.schemas" not in vscode_settings:
        vscode_settings["yaml.schemas"] = {}

    # Map extension JSON schema definitions to extension YAML files
    map_json_schemas_to_yaml(
        vscode_settings,
        project_dir_path,
        json_schemas_dir_path,
        extension_yaml_dir_path,
    )

    # Write the updated settings.json file
    with open(vscode_settings_json_file_path, "w") as f:
        vscode_settings_file_text = json.dumps(vscode_settings, indent=2)
        f.write(vscode_settings_file_text)
        logger.info(f"Updated {vscode_settings_json_file_path} with new YAML schema mappings.")


def check_json_schemas_dir_exists(json_schemas_dir_path: Path):
    """Make sure that source directory with JSON schema exists and contains valid JSON schema files"""
    if not json_schemas_dir_path.exists():
        logger.error(f"{json_schemas_dir_path} directory with JSON schema files does not exist.")
        exit(1)
    
    if not (json_schemas_dir_path / "extension.schema.json").exists():
        logger.error(f"{json_schemas_dir_path} directory does not contain extension.schema.json file.")
        exit(1)
    

def check_extension_schema_json_file_exists(
    json_schemas_dir_path: Path,
    extension_schema_json_file_path: Path,
):
    """Make sure that extension.schema.json file exists in the source directory with JSON schema"""
    schema_names = list(json_schemas_dir_path.glob("*.json"))
    if extension_schema_json_file_path not in schema_names:
        logger.error(f"extension.schema.json not found in {json_schemas_dir_path}.")
        exit(1)

    if not extension_schema_json_file_path.exists():
        logger.error(f"extension.schema.json not found in {json_schemas_dir_path}.")
        exit(1)


def check_extension_yaml_dir_exists(extension_yaml_dir_path: Path):
    """Make sure files directory with YAML files exists"""
    if not extension_yaml_dir_path.exists():
        logger.error(f"{extension_yaml_dir_path} directory with extension YAML files does not exist.")
        exit(1)


def extract_definitions_into_standalone_schemas(json_schemas_dir_path: Path):
    """Open each schema file and extract definitions into standalone schema files"""
    # Get a list of all JSON schema files in the directory
    schema_file_paths = list(json_schemas_dir_path.glob("*.json"))
    for schema_file_path in schema_file_paths:
        relative_schema_file_path = schema_file_path.relative_to(json_schemas_dir_path)
        # Get stem two times to convert extension.schema.json to extension
        parent_schema_stem = Path(schema_file_path.stem).stem 
        logger.debug(f"Processing schema file: {relative_schema_file_path}")

        with open(schema_file_path, "r") as f:
            schema_json_text = f.read()
            schema = json.loads(schema_json_text)

            # Do not process already extracted schemas
            if not str(schema.get("$id")).startswith("http"):
                # Skip
                continue

            # Collect potential new schemas to process
            new_schemas_to_process: dict[str, dict] = {}

            if "definitions" in schema:
                for d, definition in schema["definitions"].items():
                    # Check if the definition is nested
                    if "enums" == d:
                        logger.debug(f"Nested enums found in {relative_schema_file_path}.")
                        for enum_name, enum_def in definition.items():
                            logger.debug(f"Extracting enum: {enum_name}")
                            new_schemas_to_process[f"enums/{enum_name}"] = enum_def
                    elif "types" == d:
                        for type_name, type_def in definition.items():
                            logger.debug(f"Extracting type: {type_name}")
                            new_schemas_to_process[f"types/{type_name}"] = type_def
                    elif (
                        definition.get("type") == "array"
                        and "items" in definition
                        and "$ref" not in definition["items"]
                    ):
                        logger.debug(f"Extracting array item definition: {d}")
                        new_schemas_to_process[d] = definition["items"]
                    else:
                        logger.debug(f"Extracting definition: {d}")
                        new_schemas_to_process[d] = definition

            if "properties" in schema:
                for p, property in schema["properties"].items():
                    if (
                        property.get("type") == "array"
                        and "items" in property
                        and "$ref" not in property["items"]
                    ):
                        logger.debug(f"Extracting array item property: {p}")
                        new_schemas_to_process[p] = property["items"]

            if (
                schema.get("type") == "array"
                and "items" in schema
                and "$ref" not in schema["items"]
            ):
                logger.debug(f"Extracting child item from array: {relative_schema_file_path}")
                new_schemas_to_process["object"] = schema["items"]

            for name, new_schema in new_schemas_to_process.items():
                valid_name = name.replace("/", ".")
                extract_single_definition_into_standalone_schema(
                    parent_schema_stem,
                    valid_name,
                    json_schemas_dir_path,
                    new_schema,
                )


def extract_single_definition_into_standalone_schema(
    parent_schema_stem: str,
    name: str,
    json_schemas_dir_path: Path,
    definition: dict,
):
    file_name = f"{parent_schema_stem}.{name}.schema.json"
    enrich_definition_for_standalone_schema(definition, file_name)

    # Write the enriched definition to a new schema file
    d_schema_file_path = json_schemas_dir_path / file_name
    with open(d_schema_file_path, "w") as d_schema_file:
        d_schema_text = json.dumps(definition, indent=2)

        # If extracted definition contains references to sibling definitions,
        # then replace them with new extracted schema file names
        # Regex to replace "#/definitions/{name}"" reference with "{name}.schema.json"

        # Find all references to sibling definitions using regex
        for m in re.finditer(r'"#/definitions/(.+)"', d_schema_text):
            full_match = m.group(0)
            logger.debug(f"Found reference to sibling definition: {full_match}")
            catch_replacement = m.group(1).replace("/", ".")
            full_replacement = f'"{parent_schema_stem}.{catch_replacement}.schema.json"'
            logger.debug(f'Will be replaced with: {full_replacement}')
            d_schema_text = d_schema_text.replace(full_match, full_replacement)

        # Save to file
        d_schema_file.write(d_schema_text)
        logger.info(f"Extracted new schema: {file_name}")


def enrich_definition_for_standalone_schema(definition: dict, file_name: str):
    definition["$schema"] = "http://json-schema.org/draft-07/schema#"
    definition["$id"] = file_name
    definition["description"] = f"Representation of {file_name}"
    definition["additionalProperties"] = False


def read_vscode_settings_json_file(vscode_settings_json_file_path: Path):
    """Read settings.json if it exists, otherwise create an empty dictionary."""
    if vscode_settings_json_file_path.exists():
        with open(vscode_settings_json_file_path, "r") as f:
            vscode_settings_file_text = f.read()
            vscode_settings = json.loads(vscode_settings_file_text)
    else:
        vscode_settings = {}
    return vscode_settings


def map_json_schemas_to_yaml(
    vscode_settings: dict,
    project_dir_path: Path,
    extension_schema_dir_path: Path,
    extension_yaml_dir_path: Path,
):
    """Associate extension.schema.json with extension.yaml and extension.base.yaml"""
    schemas = vscode_settings.get("yaml.schemas", {})

    # Delete extension.yaml mapping
    for k, v in schemas.items():
        if "extension.yaml" in str(v):
            del schemas[k]
            break

    # If project dir is just the current directory, then resolve it
    project_dir_path = project_dir_path.resolve()

    # Make sure the directories are relative to the project directory
    extension_schema_dir_path = extension_schema_dir_path.resolve().relative_to(project_dir_path)
    extension_yaml_dir_path = extension_yaml_dir_path.resolve().relative_to(project_dir_path)

    # ------------------------------
    # Generated extension assembly
    # ------------------------------

    schemas[(extension_schema_dir_path / "extension.schema.json").as_posix()] = [
        (extension_yaml_dir_path / "extension.yaml").as_posix(),
        (extension_yaml_dir_path / "extension.base.yaml").as_posix(),
    ]

    # ------------------------------
    # Metrics
    # ------------------------------

    schemas[(extension_schema_dir_path / "extension.metrics.schema.json").as_posix()] = [
        (extension_yaml_dir_path / "metrics" / "**/*.yaml").as_posix(),
    ]

    # ------------------------------
    # Datasources
    # ------------------------------

    # gcp
    schemas[(extension_schema_dir_path / "gcp.service.schema.json").as_posix()] = [
        (extension_yaml_dir_path / "gcp" / "*.yaml").as_posix(),
    ]

    # jmx
    schemas[(extension_schema_dir_path / "jmx.group.schema.json").as_posix()] = [
        (extension_yaml_dir_path / "jmx" / "*.yaml").as_posix(),
    ]

    # processes
    schemas[(extension_schema_dir_path / "processes.object.schema.json").as_posix()] = [
        (extension_yaml_dir_path / "processes" / "*.yaml").as_posix(),
    ]

    # prometheus
    schemas[(extension_schema_dir_path / "prometheus.object.schema.json").as_posix()] = [
        (extension_yaml_dir_path / "prometheus" / "*.yaml").as_posix(),
    ]

    # snmp
    schemas[(extension_schema_dir_path / "snmp.object.schema.json").as_posix()] = [
        (extension_yaml_dir_path / "snmp" / "*.yaml").as_posix(),
    ]

    # snmptraps
    schemas[(extension_schema_dir_path / "snmptraps.object.schema.json").as_posix()] = [
        (extension_yaml_dir_path / "snmptraps" / "*.yaml").as_posix(),
    ]

    # sql
    schemas[(extension_schema_dir_path / "sql.object.schema.json").as_posix()] = [
        (extension_yaml_dir_path / "sqlDb2" / "*.yaml").as_posix(),
        (extension_yaml_dir_path / "sqlHana" / "*.yaml").as_posix(),
        (extension_yaml_dir_path / "sqlMySql" / "*.yaml").as_posix(),
        (extension_yaml_dir_path / "sqlPostgres" / "*.yaml").as_posix(),
        (extension_yaml_dir_path / "sqlOracle" / "*.yaml").as_posix(),
        (extension_yaml_dir_path / "sqlServer" / "*.yaml").as_posix(),
        (extension_yaml_dir_path / "sqlSnowflake" / "*.yaml").as_posix(),
    ]

    # wmi
    schemas[(extension_schema_dir_path / "wmi.object.schema.json").as_posix()] = [
        (extension_yaml_dir_path / "wmi" / "*.yaml").as_posix(),
    ]

    # ------------------------------
    # Topology
    # ------------------------------

    schemas[(extension_schema_dir_path / "generic.types.object.schema.json").as_posix()] = [
        (extension_yaml_dir_path / "topology" / "types" / "**/*.yaml").as_posix(),
    ]

    schemas[(extension_schema_dir_path / "generic.relationships.object.schema.json").as_posix()] = [
        (extension_yaml_dir_path / "topology" / "relationships" / "**/*.yaml").as_posix(),
    ]
    
    # ------------------------------
    # Screens
    # ------------------------------

    schemas[(extension_schema_dir_path / "extension.screens.schema.json").as_posix()] = [
        (extension_yaml_dir_path / "screens" / "**/*.yaml").as_posix(),
    ]

    # Update yaml.schemas mapping in settings.json
    vscode_settings["yaml.schemas"] = schemas


