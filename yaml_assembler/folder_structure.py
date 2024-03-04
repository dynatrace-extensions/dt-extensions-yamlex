from pathlib import Path


def ensure_folder_structure(extension_yaml_dir_path: Path, datasource_name: str | None = None):
    """Ensure the folder structure is in place."""
    # metrics
    metrics_dir_path = extension_yaml_dir_path / "metrics"
    metrics_dir_path.mkdir(parents=True, exist_ok=True)

    # datasource
    if datasource_name and datasource_name != "python":
        datasource_dir_path = extension_yaml_dir_path / datasource_name
        datasource_dir_path.mkdir(parents=True, exist_ok=True)

    # topology
    topology_dir_path = extension_yaml_dir_path / "topology"
    topology_dir_path.mkdir(parents=True, exist_ok=True)

    # topology types
    topology_types_dir_path = topology_dir_path / "types"
    topology_types_dir_path.mkdir(parents=True, exist_ok=True)

    # topology relationships
    topology_relationships_dir_path = topology_dir_path / "relationships"
    topology_relationships_dir_path.mkdir(parents=True, exist_ok=True)

    # screens
    screens_dir_path = extension_yaml_dir_path / "screens"
    screens_dir_path.mkdir(parents=True, exist_ok=True)
