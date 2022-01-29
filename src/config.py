import os
from collections import namedtuple
from typing import Dict

from dotenv import dotenv_values

dotenv_path = ".env"

config: Dict = dotenv_values(dotenv_path)

for c in config:
    if "/" in config[c]:
        config[c] = f"{os.sep.join(config[c].split('/'))}"

ENV = namedtuple("ENV", config)(**config)
