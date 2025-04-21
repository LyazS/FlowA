from typing import Dict, List, Optional, Any
from loguru import logger
from pydantic import BaseModel
from app.schemas.farequest import VarItem, ValidationError
from app.schemas.VFlowData import VFlowData
from app.schemas.VFlowRunData import RefVarItem
from app.schemas.VFNodeInterface import (
    VFNodeConnectionType,
    VFNodeFlag,
    VFNodeContentData,
    VFNodeHandleData,
    VFNodeConnectionDataType,
    VFNodeContentDataConfig,
)
from app.uisdk.VFUIDefine import *
from app.nodes import FATaskNode, FANODE_REGISTRY


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

                return [
                    RefVarItem(Nid=item.NodeId, Path=item.DataPath).model_dump_json()
                    for item in tmp_vars
                ]

        logger.error(f"Nid: {nid} [getConnectionByPath] with Invalid path: {path}")
        return None

    async def validate(
        self,
        wid: str,
        flowdata: VFlowData,
    ) -> Dict[str, ValidationError]:
        # 初始化所有节点
        for nodeinfo in flowdata.nodes:
            node = (FANODE_REGISTRY[nodeinfo.data.NType])(wid, nodeinfo, None)
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
