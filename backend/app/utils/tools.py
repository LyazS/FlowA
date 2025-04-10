import yaml
import re
from typing import Dict, Any, List, TYPE_CHECKING
from uuid_extensions import uuid7str
from functools import reduce
import hashlib
import json

if TYPE_CHECKING:
    from app.services.FARunner import FARunner
    from app.nodes.BaseNode import FABaseNode


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


def generateCacheKey(data: Dict) -> str:
    """
    生成节点的缓存键
    :param data: 任意字典
    :return: 缓存键字符串
    """
    # 将输入参数序列化为字符串
    request_str = json.dumps(data, sort_keys=True)
    # 计算哈希值以确保唯一性
    cache_key = hashlib.sha256(request_str.encode()).hexdigest()
    return cache_key


def buildCache4GenerateKey(
    node: "FABaseNode",
    cache_parentNode: bool = True,
    cache_preNodes: bool = True,
    cache_Connections: bool = True,
    cache_Payloads: bool = True,
    cache_Results: bool = True,
    cache_Config: bool = True,
    cache_Attaching: bool = True,
    cache_Nesting: bool = True,
    other: Dict = None,
) -> Dict:
    parentCacheKey = None
    if cache_parentNode:
        parentNode = node.runner().getNode(node.parentNode)
        parentCacheKey = parentNode.getCacheKey(node.id) if parentNode else None
        pass
    preNodeCacheKeys = {}
    if cache_preNodes:
        for prenode in node.preNodes:
            if preNode := node.runner().getNode(prenode.nid):
                if preNodeCacheKey := preNode.getCacheKey(node.id):
                    preNodeCacheKeys[prenode.nid] = preNodeCacheKey
                else:
                    # 如果前置节点没有缓存键，则后续也要跳过缓存
                    return None
        pass
    ResultsCache = {}
    if cache_Results:
        ResultsCache = {
            k: node.data.Results.ById[k].model_dump(exclude="Data")
            for k in node.data.Results.Order
        }
    data = {
        "wid": node.wid,
        "id": node.id,
        "data": {
            "Connections": (
                node.data.Connections.model_dump() if cache_Connections else None
            ),
            "Payloads": node.data.Payloads.model_dump() if cache_Payloads else None,
            "Results": ResultsCache,
            "Config": node.data.Config.model_dump() if cache_Config else None,
            "Attaching": (
                node.data.Attaching.model_dump()
                if node.data.Attaching and cache_Attaching
                else None
            ),
            "Nesting": (
                node.data.Nesting.model_dump()
                if node.data.Nesting and cache_Nesting
                else None
            ),
        },
        "parentCacheKey": parentCacheKey,
        "preNodeCacheKeys": preNodeCacheKeys,
        "other": other,
    }
    pass
    return data
