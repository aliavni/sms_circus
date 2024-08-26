import glob
from typing import List

import yaml


def read_sender_configs(configs_path: str = "sms_circus/sender_configs") -> List[dict]:
    configs = []
    for file_path in glob.glob(f"{configs_path}/*.yml"):
        with open(file_path) as f:
            config = yaml.safe_load(f)
            configs.append(config)

    return configs
