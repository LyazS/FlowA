import yaml
import re
from typing import Dict
from uuid_extensions import uuid7str


def read_yaml(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def replace_vars(text: str, input_args: Dict[str, str]) -> str:
    """
    替换文本中的模板变量 {{xxx}}
    """

    def replacer(match):
        var_name = match.group(1)
        return str(input_args.get(var_name, match.group(0)))

    return re.sub(r"\{\{(\w+)\}\}", replacer, text)


def getUuid():
    return uuid7str().replace("-", "")
