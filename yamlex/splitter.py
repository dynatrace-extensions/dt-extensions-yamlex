import logging
import re
from pathlib import Path

import ruamel.yaml

from yamlex.folder_structure import ensure_folder_structure
from yamlex.datasource_names import DATASOURCE_NAMES


logger = logging.getLogger(__name__)
parser = ruamel.yaml.YAML()


def split_yaml(extension_yaml_dir_path: Path) -> None:
    """Decompose a YAML file into multiple files."""
    extension_yaml_file_path = extension_yaml_dir_path / "extension.yaml"

    logger.info(f"Decomposing the central YAML file into parts: {extension_yaml_file_path}")
    with open(extension_yaml_file_path, "r") as extension_yaml_file:
        data = parser.load(extension_yaml_file)

    # Detect the datasource name
    datasource_name: str | None = None
    for name in DATASOURCE_NAMES:
        if name in data:
            datasource_name = name
            break

    logger.info(f"Datasource name detected: {datasource_name}")

    # Ensure the folder structure is in place
    ensure_folder_structure(extension_yaml_dir_path, datasource_name)
    logger.info(f"Folder structure ensured at: {extension_yaml_dir_path}")

    # Process datasource groups
    logger.info(f"Processing datasource groups...")
    if datasource_name and datasource_name != "python":
        datasource_dir_path = extension_yaml_dir_path / datasource_name

        items: list[dict] = data[datasource_name]
        for item in items:
            if datasource_name == "processes":
                item_name: str = item.get("name")
            else:
                item_name: str = item.get("group")

            if not item_name:
                logger.error(f"Item does not have a name")
                continue

            # Convert group name to a file name with only lowercase and underscores
            item_name_id = re.sub(r"[^a-z0-9_]", "_", item_name.lower())
            item_file_name = f"{item_name_id}.yaml"

            # Check whether such file already exists within the datasource directory
            search_results = list(datasource_dir_path.glob(f"**/{item_file_name}"))
            if search_results:
                logger.debug(f"Item file already exists: {search_results[0]}")
                continue

            # Extract group into a separate file
            item_file_path = datasource_dir_path / item_file_name
            with open(item_file_path, "w") as item_file:
                parser.indent(mapping=2, sequence=4, offset=2)
                parser.dump(item, item_file)
                logger.info(f"Item extracted: {item_file_path}")

    # Process metrics
    logger.info(f"Processing metrics...")
    metrics_dir_path = extension_yaml_dir_path / "metrics"
    if "metrics" in data:
        metrics: list[dict] = data["metrics"]
        for metric in metrics:
            entity_type = metric.get("key")
            if not entity_type:
                logger.error(f"Metric does not have a key: {metric}")
                continue

            metric_file_name = f"{entity_type}.yaml"

            # Check whether such file already exists within the metrics directory
            search_results = list(metrics_dir_path.glob(f"**/{metric_file_name}"))
            if search_results:
                logger.debug(f"Metric file already exists: {search_results[0]}")
                continue

            # Extract metric into a separate file
            metric_file_path = metrics_dir_path / metric_file_name
            with open(metric_file_path, "w") as metric_file:
                parser.indent(mapping=2, sequence=4, offset=2)
                parser.dump(metric, metric_file)
                logger.info(f"Metric extracted: {metric_file_path}")

    # Process screens
    logger.info(f"Processing screens...")
    screens_dir_path = extension_yaml_dir_path / "screens"
    if "screens" in data:
        screens: list[dict] = data["screens"]
        for screen in screens:
            entity_type: str = screen.get("entityType")
            if not entity_type:
                logger.error(f"Screen does not have an entity_type")
                continue

            entity_type_id = re.sub(r"[^a-z0-9_]", "_", entity_type.lower())
            screen_file_name = f"{entity_type_id}.yaml"

            # Check whether such file already exists within the screens directory
            search_results = list(screens_dir_path.glob(f"**/{screen_file_name}"))
            if search_results:
                logger.debug(f"Screen file already exists: {search_results[0]}")
                continue

            # Extract screen into a separate file
            screen_file_path = screens_dir_path / screen_file_name
            with open(screen_file_path, "w") as screen_file:
                parser.indent(mapping=2, sequence=4, offset=2)
                parser.dump(screen, screen_file)
                logger.info(f"Screen extracted: {screen_file_path}")

    # Process topology
    logger.info(f"Processing topology...")
    topology_dir_path = extension_yaml_dir_path / "topology"
    if "topology" in data:
        topology: dict = data["topology"]
        if "types" in topology:
            logger.info(f"Processing topology types...")
            types: list[dict] = topology["types"]
            types_dir_path = topology_dir_path / "types"
            for type_ in types:
                type_name = type_.get("name")
                if not type_name:
                    logger.error(f"Type does not have a name: {type_}")
                    continue

                type_name_id = re.sub(r"[^a-z0-9_]", "_", type_name.lower())
                type_file_name = f"{type_name_id}.yaml"

                # Check whether such file already exists within the types directory
                search_results = list(types_dir_path.glob(f"**/{type_file_name}"))
                if search_results:
                    logger.debug(f"Type file already exists: {search_results[0]}")
                    continue

                # Extract type into a separate file
                type_file_path = types_dir_path / type_file_name
                with open(type_file_path, "w") as type_file:
                    parser.indent(mapping=2, sequence=4, offset=2)
                    parser.dump(type_, type_file)
                    logger.info(f"Type extracted: {type_file_path}")

        if "relationships" in topology:
            logger.info(f"Processing topology relationships...")
            relationships: list[dict] = topology["relationships"]
            relationships_dir_path = topology_dir_path / "relationships"
            for relationship in relationships:
                if (
                    "fromType" not in relationship
                    or "toType" not in relationship
                    or "typeOfRelation" not in relationship
                ):
                    logger.error(f"Relationship does not have required fields: {relationship}")
                    continue

                relationship_from_id = re.sub(r"[^a-z0-9_]", "_", relationship["fromType"].lower())
                relationship_to_id = re.sub(r"[^a-z0-9_]", "_", relationship["toType"].lower())
                relationship_type_id = re.sub(r"[^a-z0-9_]", "_", relationship["typeOfRelation"].lower())

                relationship_name_id = f"{relationship_from_id}_{relationship_type_id}_{relationship_to_id}"
                relationship_file_name = f"{relationship_name_id}.yaml"

                # Check whether such file already exists within the relationships directory
                search_results = list(relationships_dir_path.glob(f"**/{relationship_file_name}"))
                if search_results:
                    logger.debug(f"Relationship file already exists: {search_results[0]}")
                    continue

                # Extract relationship into a separate file
                relationship_file_path = relationships_dir_path / relationship_file_name
                with open(relationship_file_path, "w") as relationship_file:
                    parser.indent(mapping=2, sequence=4, offset=2)
                    parser.dump(relationship, relationship_file)
                    logger.info(f"Relationship extracted: {relationship_file_path}")
