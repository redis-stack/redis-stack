import os
from typing import Union

import yaml


class Config(object):
    """Singleton of our configuration parameters"""

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(Config, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        here = os.path.dirname(__file__)
        yaml_path = os.path.abspath(os.path.join(here, "..", "config.yml"))

        with open(yaml_path, "r") as fp:
            self.CONTENT = yaml.load(fp, Loader=yaml.SafeLoader)
            # k = content.get(item)
            # if k is None:
            #     raise AttributeError(f"No key found in yaml for {item}.")
            # return k

    def get_key(self, item: str) -> Union[str, None]:
        return self.CONTENT.get(item)
