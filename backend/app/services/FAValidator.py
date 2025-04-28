from typing import Dict, List, Optional, Any, Set, Union, Tuple
from loguru import logger
from pydantic import BaseModel
from app.schemas.farequest import VarItem, ValidationError
from app.schemas.VFlowData import VFlowData
from app.schemas.VFNodeInterface import (
    VFNodeConnectionType,
    VFNodeFlag,
    VFNodeContentData,
    VFNodeHandleData,
    VFNodeConnection,
    VFNodeConnectionDataType,
    VFNodeContentDataConfig,
    RefVarItem,
    RefNodeHandleItem,
)
from app.uisdk.VFUIDefine import *
from app.nodes import FATaskNode, createRegisteredNode


class ConnectEdge(BaseModel):
    nid: str
    hid: str
    pass


class ConnectGraph(BaseModel):
    source: Dict[str, List[ConnectEdge]] = {}
    target: Dict[str, List[ConnectEdge]] = {}
    pass


class FAValidator:
    def __init__(self):
        self.nodes: Dict[str, FATaskNode] = {}
        self.connectGraph: Dict[str, ConnectGraph] = {}
        pass

    def get_handle_connections(self, nid, type_str, hid):
        """获取连接到指定handle的边"""
        if nid in self.connectGraph:
            if type_str == "source":
                return self.connectGraph[nid].source.get(hid, [])
            elif type_str == "target":
                return self.connectGraph[nid].target.get(hid, [])
        return []

    def resolve_value_by_path(self, path, data_context):
        """根据路径解析值"""
        result = data_context
        for key in path:
            if result is None:
                return None
            if hasattr(result, "get"):
                result = result.get(key)
            elif hasattr(result, key):
                result = getattr(result, key)
            else:
                return None
        return result

    def find_var_from_io(
        self,
        nid: str,
        findconnect: VFNodeConnectionType,
        hid: str,
    ) -> List[VarItem]:
        """根据节点ID、连接类型和handleID查找变量"""
        result = []
        thenode = self.nodes.get(nid)
        if not thenode:
            return result

        # 将前端的枚举映射到后端的属性名
        connection_map = {
            VFNodeConnectionType.Self: lambda: thenode.data.Connections.Self,
            VFNodeConnectionType.Attach: lambda: thenode.data.Connections.Attach,
            VFNodeConnectionType.Inputs: lambda: thenode.data.Connections.Inputs,
            VFNodeConnectionType.Outputs: lambda: thenode.data.Connections.Outputs,
        }

        # 获取连接数据
        connections = (connection_map[findconnect]()).ById
        if not connections or hid not in connections:
            return result

        connection = connections[hid].Data

        for c_data in connection.values():
            if c_data.Type == VFNodeConnectionDataType.FromInner and c_data.Path:
                path_data: VFNodeContentData = thenode.data.getContent(
                    c_data.Path.ContentName
                ).ById[c_data.Path.ContentId]
                if path_data:
                    result.append(
                        VarItem(
                            NodeId=nid,
                            NodeLabel=thenode.data.Label,
                            DataPath=c_data.Path,
                            DataLabel=path_data.Label,
                            DataType=path_data.Type,
                        )
                    )
            elif c_data.Type == VFNodeConnectionDataType.FromOuter and c_data.HandleId:
                edges = self.get_handle_connections(nid, "target", c_data.HandleId)
                for edge in edges:
                    src_nid = edge.nid
                    src_handle = edge.hid
                    result.extend(
                        self.recursive_find_variables(src_nid, "Outputs", [src_handle])
                    )
            elif c_data.Type == VFNodeConnectionDataType.FromAttached and c_data.ANode:
                for aname, hdata in c_data.ANode.items():
                    anode_nid = thenode.data.Nesting.ANodes[aname].Nid
                    if anode := self.nodes.get(anode_nid, None):
                        result.extend(
                            self.recursive_find_variables(
                                anode.id, hdata.ConnectionType, [hdata.HandleId]
                            )
                        )
            elif (
                c_data.Type == VFNodeConnectionDataType.FromParent
                and thenode.parentNode
            ):
                # 匹配前端的父节点处理逻辑
                result.extend(
                    self.recursive_find_variables(
                        thenode.parentNode, "Attach", [c_data.HandleId]
                    )
                )

        return result

    def recursive_find_variables(
        self,
        nid: str,
        handle_type: VFNodeConnectionType,
        handles: List[str] = None,
    ) -> List[VarItem]:
        """递归查找变量，与前端代码结构一致"""
        result = []
        if nid not in self.nodes:
            return result

        thenode = self.nodes[nid]

        # 如果没有提供handles，根据handleType获取所有handles
        if handles is None:
            connection_map = {
                VFNodeConnectionType.Self: lambda: thenode.data.Connections.Self.Order,
                VFNodeConnectionType.Attach: lambda: thenode.data.Connections.Attach.Order,
                VFNodeConnectionType.Inputs: lambda: thenode.data.Connections.Inputs.Order,
                VFNodeConnectionType.Outputs: lambda: thenode.data.Connections.Outputs.Order,
            }

            if getter := connection_map.get(handle_type):
                handles = list(getter())
            else:
                handles = []

        # 对每个handle调用find_var_from_io
        for hid in handles:
            result.extend(self.find_var_from_io(nid, handle_type, hid))

        return result

    # 缓存连接查询结果
    _cache_connections_by_args: Dict[str, Any] = {}

    async def getConnectionsByArgs(self, thisnid: str, args: List[str]) -> Optional[
        Union[
            List[str],
            Dict[str, Dict[str, List[str]]],
            List[RefVarItem],
            List[RefNodeHandleItem],
        ]
    ]:
        """
        根据参数获取连接信息，类似于前端的getConnectionsByArgs函数

        参数格式：
        ====================================================
        节点层级（Node Level）
        ====================================================
        --node: 必填，节点层级
            CONNECT_CUR_NODE: 当前节点
            CONNECT_PARENT_NODE: 父节点
            CONNECT_CHILD_NODE: 子节点
                --child: 如果node是CONNECT_CHILD_NODE则必填
                    CONNECT_ALL_DATA: 所有子节点
                    string: 特定子节点名称
            CONNECT_PRE_NODE: 前置节点
                --inhid: 如果node是CONNECT_PRE_NODE则必填
                    CONNECT_ALL_DATA: 所有输入handles
                    string: 特定输入handle ID
        ====================================================
        句柄层级（Handle Level）
        ====================================================
        --handle: 非必填，句柄类型
            VFNodeConnectionType: 特定类型的handles
            CONNECT_ALL_DATA: 所有类型的handles
        --stricthid: 非必填，只获取与本节点有链接的handle
            string: 本节点的输入handle ID
        ====================================================
        变量层级（Variable Level）
        ====================================================
        --hid: 非必填，handle ID
            CONNECT_ALL_DATA: 所有handles
            string: 特定handle ID
        ====================================================
        --level: 必填，输出层级
            CONNECT_NODE_LEVEL: 节点层级
            CONNECT_HANDLE_LEVEL: 句柄层级
            CONNECT_VAR_LEVEL: 变量层级
        ====================================================
        --notop: 非必填，为true可用于在只有一个node的时候，去掉根节点
        ====================================================
        --outfmt: 必填，输出格式
            CONNECT_ALL_DATA：表示输出对应原始数据
                节点层级 [<node_id>]
                句柄层级 {<node_id>: {<handle_type>: [<handle_id>]}}
                变量层级 [<RefVarItem>]
            CONNECT_DATA_TO_SELECT: 数组形式
                节点层级 [<node_id>]
                句柄层级 [<node_id>, <handle_type>, <handle_id>][]
                变量层级 [<RefVarItem>]
        """
        # 解析参数
        # 使用缓存键
        cache_key = f"{thisnid}-{'-'.join(args)}"
        if cache_key in self._cache_connections_by_args:
            return self._cache_connections_by_args[cache_key]

        parsed_args = {
            "level": None,
            "node": None,
            "child": None,
            "inhid": None,
            "handle": None,
            "stricthid": None,
            "hid": None,
            "outfmt": None,
            "notop": False,
        }

        # 解析参数列表
        i = 0
        while i < len(args):
            arg = args[i]
            if arg.startswith("--"):
                key = arg[2:]
                if key in parsed_args:
                    # 对于布尔标志，直接设置为true
                    if key == "notop":
                        parsed_args[key] = True
                        i += 1
                        continue

                    # 检查是否有下一个参数作为值
                    if i + 1 >= len(args):
                        i += 1
                        continue
                    next_arg = args[i + 1]

                    # 确保下一个参数不是另一个选项
                    if next_arg.startswith("--"):
                        i += 1
                        continue

                    parsed_args[key] = next_arg
                    i += 2  # 跳过已处理的值
                    continue
            i += 1

        # 验证必要参数
        if (
            not parsed_args["node"]
            or not parsed_args["level"]
            or not parsed_args["outfmt"]
        ):
            logger.error(
                f"Nid: {thisnid} [getConnectionsByArgs] Missing required arguments"
            )
            return None

        # ====================================================
        # 节点层级（Node Level）
        # ====================================================
        node_ids: List[str] = []
        node_type = parsed_args["node"]

        if node_type == CONNECT_CUR_NODE:
            # 当前节点
            node_ids.append(thisnid)
        elif node_type == CONNECT_PARENT_NODE:
            # 父节点
            thenode = self.nodes.get(thisnid)
            if thenode and hasattr(thenode, "parentNode") and thenode.parentNode:
                node_ids.append(thenode.parentNode)
        elif node_type == CONNECT_CHILD_NODE:
            # 子节点
            child_name = parsed_args["child"]
            if not child_name:
                return None

            thenode = self.nodes.get(thisnid)
            if thenode and hasattr(thenode.data, "Nesting") and thenode.data.Nesting:
                if child_name == CONNECT_ALL_DATA:
                    # 所有子节点
                    for anode in thenode.data.Nesting.ANodes.values():
                        if hasattr(anode, "Nid") and anode.Nid:
                            node_ids.append(anode.Nid)
                else:
                    # 特定子节点
                    if child_name in thenode.data.Nesting.ANodes:
                        anode = thenode.data.Nesting.ANodes[child_name]
                        if hasattr(anode, "Nid") and anode.Nid:
                            node_ids.append(anode.Nid)
        elif node_type == CONNECT_PRE_NODE:
            # 前置节点
            in_handle = parsed_args["inhid"]
            if not in_handle:
                return None

            in_handles = [in_handle] if in_handle != CONNECT_ALL_DATA else []

            # 如果是CONNECT_ALL_DATA，获取所有输入handles
            if in_handle == CONNECT_ALL_DATA:
                thenode = self.nodes.get(thisnid)
                if thenode:
                    in_handles = thenode.data.Connections.Inputs.Order

            # 获取所有连接到这些输入handles的源节点
            for handle in in_handles:
                edges = self.get_handle_connections(thisnid, "target", handle)
                for edge in edges:
                    node_ids.append(edge.nid)
        else:
            # 直接使用节点ID
            node_ids.append(node_type)

        # 如果是节点层级，直接返回结果
        if parsed_args["level"] == CONNECT_NODE_LEVEL:
            result = None
            if parsed_args["outfmt"] == CONNECT_ALL_DATA:
                # 返回节点对象
                result = [self.nodes.get(nid) for nid in node_ids if nid in self.nodes]
            elif parsed_args["outfmt"] == CONNECT_DATA_TO_SELECT:
                # 返回节点ID列表
                result = node_ids

            self._cache_connections_by_args[cache_key] = result
            return result

        # ====================================================
        # 句柄层级（Handle Level）
        # ====================================================
        handle_type = parsed_args["handle"]
        if not handle_type:
            handle_type = CONNECT_ALL_DATA

        handle_types: List[VFNodeConnectionType] = []
        handle_items: List[RefNodeHandleItem] = []

        # 确定要处理的handle类型
        if handle_type == CONNECT_ALL_DATA:
            # 所有handle类型
            handle_types = [
                VFNodeConnectionType.Self,
                VFNodeConnectionType.Attach,
                VFNodeConnectionType.Inputs,
                VFNodeConnectionType.Outputs,
                VFNodeConnectionType.CallbackUsers,
                VFNodeConnectionType.CallbackFuncs,
            ]
        else:
            # 特定handle类型
            for conn_type in VFNodeConnectionType:
                if handle_type == conn_type:
                    handle_types.append(conn_type)
                    break

        # 处理stricthid参数（只获取与本节点有链接的handle）
        strict_items: List[Tuple[str, str]] = []
        if parsed_args["stricthid"]:
            edges = self.get_handle_connections(
                thisnid, "target", parsed_args["stricthid"]
            )
            for edge in edges:
                strict_items.append((edge.nid, edge.hid))

        # 收集所有符合条件的handles
        for node_id in node_ids:
            node = self.nodes.get(node_id)
            if not node:
                continue

            for conn_type in handle_types:
                # 获取该类型的所有handles
                if not hasattr(node.data.Connections, conn_type):
                    continue

                connections: VFNodeConnection = getattr(
                    node.data.Connections, conn_type
                )
                connections_order = connections.Order
                for hid in connections_order:
                    # 如果有stricthid限制，检查是否符合条件
                    if parsed_args["stricthid"] and (node_id, hid) not in strict_items:
                        continue

                    handle_items.append(
                        RefNodeHandleItem(
                            Node=node_id, HandleType=conn_type, Handle=hid
                        )
                    )

        # 如果是句柄层级，返回结果
        if parsed_args["level"] == CONNECT_HANDLE_LEVEL:
            result = None
            if parsed_args["outfmt"] == CONNECT_ALL_DATA:
                # 返回句柄字典
                res: Dict[str, Dict[str, List[str]]] = {}
                for item in handle_items:
                    nid, ctype, hid = item.Node, item.HandleType, item.Handle
                    if nid not in res:
                        res[nid] = {}
                    if ctype not in res[nid]:
                        res[nid][ctype] = []
                    res[nid][ctype].append(hid)

                # 处理notop参数
                if parsed_args["notop"] and len(res) == 1:
                    nid = list(res.keys())[0]
                    if len(res[nid]) == 1:
                        ctype = list(res[nid].keys())[0]
                        result = res[nid][ctype]
                    else:
                        result = res[nid]
                else:
                    result = res
            elif parsed_args["outfmt"] == CONNECT_DATA_TO_SELECT:
                # 返回句柄项列表
                result = handle_items

            self._cache_connections_by_args[cache_key] = result
            return result

        # ====================================================
        # 变量层级（Variable Level）
        # ====================================================
        handle_id = parsed_args["hid"]
        if not handle_id:
            handle_id = CONNECT_ALL_DATA

        var_items: List[VarItem] = []
        for item in handle_items:
            nid, ctype, hid = item.Node, item.HandleType, item.Handle
            if handle_id == CONNECT_ALL_DATA or handle_id == hid:
                var_items.extend(self.find_var_from_io(nid, ctype, hid))

        # 去重
        unique_var_items: List[VarItem] = []
        seen_paths = set()
        for item in var_items:
            path_key = (
                f"{item.NodeId}-{item.DataPath.ContentName}-{item.DataPath.ContentId}"
            )
            if path_key not in seen_paths:
                seen_paths.add(path_key)
                unique_var_items.append(item)

        # 如果是变量层级，返回结果
        if parsed_args["level"] == CONNECT_VAR_LEVEL:
            result = None
            if (
                parsed_args["outfmt"] == CONNECT_ALL_DATA
                or parsed_args["outfmt"] == CONNECT_DATA_TO_SELECT
            ):
                # 转换为RefVarItem
                ref_var_items = [
                    RefVarItem(Nid=item.NodeId, Path=item.DataPath)
                    for item in unique_var_items
                ]
                result = ref_var_items

            self._cache_connections_by_args[cache_key] = result
            return result

        return None

    async def getConnectionByPath(self, nid: str, path: List[str | int]):
        if path is not None and len(path) > 0:
            if path[0] == CONNECT_DATA_TO_SELECT and len(path) >= 2:
                tmp_vars = []
                ctype = VFNodeConnectionType.Self
                if path[1] == "Self":
                    ctype = VFNodeConnectionType.Self
                elif path[1] == "Attach":
                    ctype = VFNodeConnectionType.Attach
                elif path[1] == "Inputs":
                    ctype = VFNodeConnectionType.Inputs
                elif path[1] == "Outputs":
                    ctype = VFNodeConnectionType.Outputs
                if path[2]:
                    tmp_vars = self.recursive_find_variables(nid, ctype, [path[2]])
                else:
                    tmp_vars = self.recursive_find_variables(nid, ctype)

                return set(
                    [
                        RefVarItem(
                            Nid=item.NodeId, Path=item.DataPath
                        ).model_dump_json()
                        for item in tmp_vars
                    ]
                )

        logger.error(f"Nid: {nid} [getConnectionByPath] with Invalid path: {path}")
        return None

    async def validate(
        self,
        wid: str,
        flowdata: VFlowData,
    ) -> Dict[str, ValidationError]:
        # 初始化所有节点
        for nodeinfo in flowdata.nodes:
            node = createRegisteredNode(nodeinfo.data.NType, wid, nodeinfo, None)
            self.nodes[nodeinfo.id] = node
            pass

        for edgeinfo in flowdata.edges:
            if edgeinfo.source in self.nodes and edgeinfo.target in self.nodes:
                source_handle = edgeinfo.sourceHandle
                target_handle = edgeinfo.targetHandle
                if edgeinfo.source not in self.connectGraph:
                    self.connectGraph[edgeinfo.source] = ConnectGraph()
                    pass
                if source_handle not in self.connectGraph[edgeinfo.source].source:
                    self.connectGraph[edgeinfo.source].source[source_handle] = []
                    pass
                self.connectGraph[edgeinfo.source].source[source_handle].append(
                    ConnectEdge(nid=edgeinfo.target, hid=target_handle)
                )
                pass
                if edgeinfo.target not in self.connectGraph:
                    self.connectGraph[edgeinfo.target] = ConnectGraph()
                    pass
                if target_handle not in self.connectGraph[edgeinfo.target].target:
                    self.connectGraph[edgeinfo.target].target[target_handle] = []
                    pass
                self.connectGraph[edgeinfo.target].target[target_handle].append(
                    ConnectEdge(nid=edgeinfo.source, hid=source_handle)
                )
                pass

        # 逐个节点验证，主要验证变量是否合法
        validations: List[ValidationError] = []
        for nid in self.nodes.keys():
            node = self.nodes[nid]
            validation = await node.validate(self)
            if validation:
                validations.append(validation)
        pass
        return validations
