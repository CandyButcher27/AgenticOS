import yaml


def load_catalog(path: str = "catalog.yaml") -> list[dict]:
    with open(path, "r") as f:
        return yaml.safe_load(f) or []


def filter_catalog(catalog: list[dict], available_providers: set[str]) -> list[dict]:
    return [entry for entry in catalog if entry["provider"] in available_providers]
