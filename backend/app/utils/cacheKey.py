from typing import Dict, List, Tuple, TYPE_CHECKING
import hashlib
import json
from app.schemas.VFlowRunData import (
    VFNodeCacheKey,
    VFNodeCacheKeyBefore,
    VFNodeCacheKeyAfter,
)

if TYPE_CHECKING:
    from app.nodes.BaseNode import FABaseNode


def generateCacheKey(data: Dict) -> str:
    """
    生成节点的缓存键
    :param data: 任意字典
    """
    # 将输入参数序列化为字符串
    if data is None:
        raise ValueError("Data cannot be None")
    request_str = json.dumps(data, sort_keys=True)
    # 计算哈希值以确保唯一性
    return hashlib.sha256(request_str.encode()).hexdigest()


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
) -> VFNodeCacheKey:
    cacheBefore = VFNodeCacheKeyBefore.Load
    cacheAfter = VFNodeCacheKeyAfter.Save

    parentCacheKey = None
    if cache_parentNode:
        if parentNode := node.runner().getNode(node.parentNode):
            # 父节点可以控制子节点的缓存策略
            childCacheKey = parentNode.getCacheKey(node.id)
            if childCacheKey.Before == VFNodeCacheKeyBefore.Load:
                parentCacheKey = childCacheKey.Key
                cacheAfter = childCacheKey.After
            else:
                return VFNodeCacheKey(Before=VFNodeCacheKeyBefore.Skip)
            pass

        pass
    preNodeCacheKeys = {}
    if cache_preNodes:
        for prenode in node.preNodes:
            if preNode := node.runner().getNode(prenode.nid):
                preNodeCacheKey = preNode.getCacheKey(node.id)
                if preNodeCacheKey.Before == VFNodeCacheKeyBefore.Load:
                    preNodeCacheKeys[prenode.nid] = preNodeCacheKey.Key
                else:
                    # 如果前置节点跳过缓存，则后续也要跳过缓存
                    return VFNodeCacheKey(Before=VFNodeCacheKeyBefore.Skip)
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
    return VFNodeCacheKey(
        Before=cacheBefore,
        Key=generateCacheKey(data),
        After=cacheAfter,
    )
