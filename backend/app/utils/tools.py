import yaml
import re
from typing import Dict, Any, List, TYPE_CHECKING
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


def getNestedLayout(nid: str):
    # matches = re.findall(r"#(\w+)", nid)
    # return [int(x) if x.isdigit() else x for x in matches]
    _, nested = regexMatchNodeId(nid)
    return nested


def generateNodeId() -> str:
    return f"NID{{{getUuid()}}}"


def regexMatchOriginalNodeId(nid: str) -> str:
    main_match = re.match(r"^NID\{([^}]+)\}", nid)
    if not main_match:
        raise ValueError(f"Invalid node id {nid}")
    return main_match.group(1)


def regexMatchNodeId(nid: str) -> tuple[str | Any, List[Any]]:
    # 匹配整个字符串结构，并提取中间内容
    main_match = re.match(r"^NID\{([^}]+)\}", nid)
    if not main_match:
        raise ValueError(f"Invalid node id {nid}")

    content = main_match.group(1)
    id_part = content.split("#")[0]  # 提取 id（第一个 # 之前的部分）

    # 匹配所有非空的嵌套说明（# 后至少一个字符）
    nested = re.findall(r"#([^#]+)", content)
    nested = [int(x) if x.isdigit() else x for x in nested]
    return (f"NID{{{id_part}}}", nested)


def concatNestedNodeId(id_str: str, nested: list) -> str:
    # Step 1: 验证并提取原始 id 的内容
    id_match = re.match(r"^NID\{([^}]+)\}", id_str)
    if not id_match:
        raise ValueError(f"Invalid node id {id_str}")

    # Step 2: 获取基础内容
    base_content = id_match.group(1)

    # Step 3: 拼接 nested 参数
    nested_part = "#" + "#".join(map(str, nested)) if nested else ""

    # Step 4: 组装完整结构
    return f"NID{{{base_content}{nested_part}}}"
