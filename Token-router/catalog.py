import os
import yaml

DEFAULT_CATALOG_PATH = os.path.join(os.path.dirname(__file__), "catalog.yaml")


def load_catalog(path: str = DEFAULT_CATALOG_PATH) -> list[dict]:
    with open(path, "r") as f:
        return yaml.safe_load(f) or []


def filter_catalog(catalog: list[dict], available_providers: set[str]) -> list[dict]:
    return [entry for entry in catalog if entry["provider"] in available_providers]
