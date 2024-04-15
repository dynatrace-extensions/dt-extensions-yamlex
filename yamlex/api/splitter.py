import logging
import re
from pathlib import Path
from typing import Union

import ruamel.yaml


logger = logging.getLogger(__name__)

DATASOURCE_NAMES = [
    "gcp",
    "jmx",
    "python",
    "processes",
    "snmp",
    "snmptraps",
    "sqlDb2",
    "sqlHana",
    "sqlMySql",
    "sqlOracle",
    "sqlPostgres",
    "sqlServer",
    "sqlSnowflake",
    "wmi",
]


def split_yaml(
    source_file_path: Path,
    target_dir_path: Path,
) -> dict[Path, Union[dict, list]]:
    """Decompose a YAML file into multiple files."""
    parts_to_write: dict[Path, Union[dict, list]] = dict()

    logger.info(f"Decomposing the central YAML file into parts: {source_file_path}")
    with open(source_file_path, "r") as extension_yaml_file:
        parser = ruamel.yaml.YAML()
        data: dict = parser.load(extension_yaml_file)

    # Process datasource
    logger.info(f"Processing datasource...")
    datasource = extract_datasource(data, target_dir_path)
    parts_to_write.update(datasource)

    # Process metrics
    logger.info(f"Processing metrics...")
    metrics_dir_path = target_dir_path / "metrics"
    metrics = extract_metrics(data, metrics_dir_path)
    parts_to_write.update(metrics)

    # Process screens
    logger.info(f"Processing screens...")
    screens_dir_path = target_dir_path / "screens"
    screens = extract_screens(data, screens_dir_path)
    parts_to_write.update(screens)

    # Process topology
    logger.info(f"Processing topology...")
    topology_dir_path = target_dir_path / "topology"
    topology = extract_topology(data, topology_dir_path)
    parts_to_write.update(topology)
    
    # Dump the rest into the index file
    index_yaml_file_path = target_dir_path / "index.yaml"
    parts_to_write[index_yaml_file_path] = data
    logger.info(f"Index file extracted: {index_yaml_file_path}")

    # Return collected summary
    return parts_to_write


def extract_datasource(
    extension: dict,
    target_dir_path: Path
) -> dict[Path, dict]:
    paths_to_write = {}

    # Detect the datasource name
    datasource_name: str | None = None
    datasource: dict | list | None = None
    for name in DATASOURCE_NAMES:
        if name in extension:
            datasource_name = name
            datasource = extension.pop(datasource_name)
            break

    if datasource_name:
        logger.info(f"Datasource name detected: {datasource_name}")
    else:
        logger.error("Datasource definition not found")
        return paths_to_write
    
    datasource_dir_path = target_dir_path / datasource_name
    
    if datasource_name == "python":
        python_index_yaml_path = datasource_dir_path / "index.yaml"
        paths_to_write[python_index_yaml_path] = datasource

    elif datasource_name == "processes":
        for process in datasource:
            process_name = process.get("name")
            if not process_name:
                logger.error("Process does not have a name")
                continue

            process_file_name = sanitize_file_stem(process_name)
            process_file_path = datasource_dir_path / f"-{process_file_name}.yaml"
            paths_to_write[process_file_path] = process
            logger.info(f"Process extracted: {process_file_path}")

    else:
        for group in datasource:
            group_name = group.get("group")
            if not group_name:
                logger.error("Group does not have a name")
                continue

            subgroups = group.pop("subgroups", None)
            # If subgroups exist, split them into different files
            if isinstance(subgroups, list):
                group_file_name = sanitize_file_stem(group_name)
                group_dir_path = datasource_dir_path / "groups" / group_file_name
                for subgroup in subgroups:
                    subgroup_name = subgroup.get("subgroup")
                    if not subgroup_name:
                        logger.error("Subgroup does not have a name")
                        continue

                    subgroup_file_name = sanitize_file_stem(subgroup_name)
                    subgroup_file_path = group_dir_path / "subgroups" / f"-{subgroup_file_name}.yaml"
                    paths_to_write[subgroup_file_path] = subgroup
                    logger.info(f"Subgroup extracted: {subgroup_file_path}")

                group_file_path = group_dir_path / "index.yaml"
                paths_to_write[group_file_path] = group
                logger.info(f"Group extracted: {group_file_path}")

            # If subgroups do not exist, write each group into
            # individual files.
            else:
                group_file_name = sanitize_file_stem(group_name)
                group_file_path = datasource_dir_path / f"-{group_file_name}.yaml"
                paths_to_write[group_file_path] = group
                logger.info(f"Group extracted: {group_file_path}")

    return paths_to_write


def extract_metrics(extension: dict, metrics_dir_path: Path) -> dict[Path, dict]:
    paths_to_write = {}
    if not isinstance(extension.get("metrics"), list):
        return paths_to_write

    metrics: list[dict] = extension.pop("metrics")
    for metric in metrics:
        metric_key = metric.get("key")
        if not metric_key:
            logger.error(f"Metric does not have a 'key': {metric}")
            continue

        metric_file_name = sanitize_file_stem(metric_key)

        # Extract metric into a separate file
        metric_file_path = metrics_dir_path / f"-{metric_file_name}.yaml"
        paths_to_write[metric_file_path] = metric
        logger.info(f"Metric extracted: {metric_file_path}")

    return paths_to_write


def extract_screens(extension: dict, screens_dir_path: Path) -> dict[Path, dict]:
    paths_to_write = {}
    if not isinstance(extension.get("screens"), list):
        return paths_to_write

    screens: list[dict] = extension.pop("screens")
    for screen in screens:
        entity_type: str = screen.get("entityType")
        if not entity_type:
            logger.error(f"Screen does not have an entity_type")
            continue
            
        screen_file_name = sanitize_file_stem(entity_type)

        # Extract screen into a separate file
        screen_file_path = screens_dir_path / f"-{screen_file_name}.yaml"
        paths_to_write[screen_file_path] = screen
        logger.info(f"Screen extracted: {screen_file_path}")

    return paths_to_write


def extract_topology(extension: dict, topology_dir_path: Path) -> dict[Path, dict]:
    paths_to_write = {}
    if not isinstance(extension.get("topology"), dict):
        return paths_to_write
    
    topology: dict = extension.pop("topology")

    types_dir_path = topology_dir_path / "types"
    types = extract_types(topology, types_dir_path)
    paths_to_write.update(types)

    relationships_dir_path = topology_dir_path / "relationships"
    relationships = extract_relationships(topology, relationships_dir_path)
    paths_to_write.update(relationships)

    return paths_to_write


def extract_types(topology: dict, types_dir_path: Path) -> dict[Path, dict]:
    paths_to_write = {}
    if not isinstance(topology.get("types"), list):
        return paths_to_write
    
    types: list[dict] = topology.pop("types")
    for type_ in types:
        type_name = type_.get("name")
        if not type_name:
            logger.error(f"Type does not have a name: {type_}")
            continue

        type_file_name = sanitize_file_stem(type_name)

        # Extract type into a separate file
        type_file_path = types_dir_path / f"-{type_file_name}.yaml"
        paths_to_write[type_file_path] = type_
        logger.info(f"Type extracted: {type_file_path}")

    return paths_to_write


def extract_relationships(topology, relationships_dir_path: Path) -> dict[Path, dict]:
    paths_to_write = {}
    if not isinstance(topology.get("relationships"), list):
        return paths_to_write
    
    relationships: list[dict] = topology.pop("relationships")
    for relationship in relationships:
        if (
            "fromType" not in relationship
            or "toType" not in relationship
            or "typeOfRelation" not in relationship
        ):
            logger.error(f"Relationship does not have required fields: {relationship}")
            continue

        relationship_file_name = sanitize_file_stem(
            (
                f"{relationship['fromType']}_"
                f"{relationship['typeOfRelation']}_"
                f"{relationship['toType']}"
            ),
        )

        # Extract relationship into a separate file
        relationship_file_path = relationships_dir_path / f"-{relationship_file_name}.yaml"
        paths_to_write[relationship_file_path] = relationship
        logger.info(f"Relationship extracted: {relationship_file_path}")

    return paths_to_write


def sanitize_file_stem(stem: str) -> Path:
    valid_id = re.sub(r"[^a-z0-9\.]", "_", stem.lower())
    return valid_id
