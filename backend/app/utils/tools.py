import yaml
import re
from typing import Dict, Any
from uuid_extensions import uuid7str
from functools import reduce


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


def reduceGet(data, path):
    def safe_get(obj, key):
        try:
            # 先尝试字典类型的访问
            if isinstance(obj, dict):
                return obj.get(key)

            # 处理数字索引的序列类型（列表/元组）
            if isinstance(obj, (list, tuple)):
                try:
                    # 尝试将key转换为整数索引
                    index = int(key)
                    if 0 <= index < len(obj):
                        return obj[index]
                except (ValueError, TypeError):
                    pass
                return None

            # 尝试作为对象属性访问
            attr = str(key)  # 确保属性名是字符串类型
            if hasattr(obj, attr):
                return getattr(obj, attr)

            # 最后尝试通用的__getitem__访问
            try:
                return obj[key]
            except (KeyError, IndexError, TypeError):
                return None

        except Exception as e:
            # 捕获其他所有异常情况
            return None

    return reduce(safe_get, path, data)
