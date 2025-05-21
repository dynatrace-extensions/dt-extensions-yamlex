import importlib.metadata
import re
from pathlib import Path


def get_version() -> None:
    version = "0.0.0"
    try:
        metadata = importlib.metadata.metadata("yamlex")
        version = metadata["Version"]
    except importlib.metadata.PackageNotFoundError:
        pyproject_file_path = Path(__file__).parent.parent / "pyproject.toml"
        if pyproject_file_path.exists() and pyproject_file_path.is_file():
            with open(pyproject_file_path) as f:
                content = f.read()
                match_ = re.search(r"version\s*=\s*(.+)", content)
                if match_:
                    version_group = match_.group(1)
                    version = version_group.strip("\"")

    return version
