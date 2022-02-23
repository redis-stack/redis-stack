import os

import yaml


def get_key(item: str) -> str:
    """Return the key specified, from the yaml file."""

    here = os.path.dirname(__file__)
    yaml_path = os.path.abspath(os.path.join(here, "..", "config.yml"))

    with open(yaml_path, "r") as fp:
        content = yaml.load(fp, Loader=yaml.SafeLoader)
        k = content.get(item)
        if k is None:
            raise AttributeError(f"No key found in yaml for {item}.")
        return k
