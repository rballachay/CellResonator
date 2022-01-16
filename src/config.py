from collections import namedtuple
from typing import Dict

from dotenv import dotenv_values

dotenv_path = ".env"

config: Dict = dotenv_values(dotenv_path)
ENV = namedtuple("ENV", config)(**config)
