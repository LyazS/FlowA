from typing import Dict, List, Optional, Any
from loguru import logger
from pydantic import BaseModel
from app.schemas.farequest import VarItem, ValidationError
from app.schemas.vfnode import VFlowData
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
            # if type_str == "source" and hid in self.connectGraph[nid]["source"]:
            #     return self.connectGraph[nid]["source"][hid]
            # elif type_str == "target" and hid in self.connectGraph[nid]["target"]:
            #     return self.connectGraph[nid]["target"][hid]
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

    # def recursive_find_variables(
    #     self,
    #     nid: str,
    #     find_self: List[str] = [],
    #     find_attach: List[str] = [],
    #     find_next: List[str] = [],
    #     find_all_input: bool = False,
    #     find_input: List[str] = None,
    #     find_all_output: bool = False,
    #     find_output: List[str] = None,
    # ) -> List[VarItem]:
    #     if find_input is None:
    #         find_input = []
    #     if find_output is None:
    #         find_output = []

    #     result = []
    #     the_node = self.nodes[nid]

    #     if find_all_input:
    #         find_input = list(the_node.data.connections.inputs.keys())
    #     if find_all_output:
    #         find_output = list(the_node.data.connections.outputs.keys())

    #     for hid in find_self:
    #         result.extend(self.find_var_from_io(nid, "self", hid))
    #     for hid in find_attach:
    #         result.extend(self.find_var_from_io(nid, "attach", hid))
    #     for hid in find_next:
    #         result.extend(self.find_var_from_io(nid, "next", hid))
    #     for hid in find_input:
    #         result.extend(self.find_var_from_io(nid, "inputs", hid))
    #     for hid in find_output:
    #         result.extend(self.find_var_from_io(nid, "outputs", hid))

    #     return result

    # def find_var_from_io(
    #     self,
    #     nid: str,
    #     findconnect: str,
    #     hid: str,
    # ) -> List[VarItem]:
    #     result = []
    #     thenode = self.nodes[nid]  # 假设这个函数在其他地方定义

    #     # 根据类型获取connection数据
    #     if (
    #         findconnect == "self"
    #         and thenode.data.connections.self != None
    #         and hid in thenode.data.connections.self
    #     ):
    #         connection = thenode.data.connections.self[hid].data
    #     elif (
    #         findconnect == "attach"
    #         and thenode.data.connections.attach != None
    #         and hid in thenode.data.connections.attach
    #     ):
    #         connection = thenode.data.connections.attach[hid].data
    #     elif (
    #         findconnect == "next"
    #         and thenode.data.connections.next != None
    #         and hid in thenode.data.connections.next
    #     ):
    #         connection = thenode.data.connections.next[hid].data
    #     elif (
    #         findconnect == "inputs"
    #         and thenode.data.connections.inputs != None
    #         and hid in thenode.data.connections.inputs
    #     ):
    #         connection = thenode.data.connections.inputs[hid].data
    #     elif (
    #         findconnect == "outputs"
    #         and thenode.data.connections.outputs != None
    #         and hid in thenode.data.connections.outputs
    #     ):
    #         connection = thenode.data.connections.outputs[hid].data
    #     else:
    #         return result

    #     for c_data in connection.values():
    #         if c_data.type == VFNodeConnectionDataType.FromInner:
    #             result.append(
    #                 VarItem(
    #                     nodeId=nid,
    #                     nlabel=thenode.data.label,
    #                     dpath=c_data.path,
    #                     dlabel=thenode.data.getContent(c_data.path[0])
    #                     .byId[c_data.path[1]]
    #                     .label,
    #                     dkey=thenode.data.getContent(c_data.path[0])
    #                     .byId[c_data.path[1]]
    #                     .key,
    #                     dtype=thenode.data.getContent(c_data.path[0])
    #                     .byId[c_data.path[1]]
    #                     .type,
    #                 )
    #             )

    #         elif c_data.type == VFNodeConnectionDataType.FromOuter:
    #             # 对于上一个节点，递归搜索上个节点的对应输出handle
    #             in_hid = c_data.inputKey
    #             edges = self.get_handle_connections(nid, "target", in_hid)
    #             for edge in edges:
    #                 src_nid = edge["nid"]
    #                 src_hid = edge["hid"]
    #                 result.extend(
    #                     self.recursive_find_variables(
    #                         src_nid, [], [], [], False, [], False, [src_hid]
    #                     )
    #                 )

    #         elif c_data.type == VFNodeConnectionDataType.FromAttached:
    #             # 对于子节点的处理
    #             result.extend(
    #                 self.recursive_find_variables(
    #                     thenode.data.nesting.attached_nodes[c_data.atype].nid,
    #                     (
    #                         ["self"]
    #                         if c_data.atype
    #                         == VFNodeConnectionDataAttachedType.attached_node_output
    #                         else []
    #                     ),
    #                     [],
    #                     [],
    #                     False,
    #                     [],
    #                     c_data.atype
    #                     == VFNodeConnectionDataAttachedType.attached_node_input,
    #                     [],
    #                 )
    #             )

    #         elif c_data.type == VFNodeConnectionDataType.FromParent:
    #             # 如果是父节点，递归搜索父节点的所有输入handle
    #             result.extend(
    #                 self.recursive_find_variables(
    #                     thenode.parentNode, [], ["attach"], [], True, [], False, []
    #                 )
    #             )

    #     return result

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
        connections = connection_map[findconnect]()
        if not connections or hid not in connections:
            return result

        connection = connections[hid].Data

        for c_data in connection.values():
            if c_data.Type == VFNodeConnectionDataType.FromInner and c_data.Path:
                path_data: VFNodeContentData = self.resolve_value_by_path(
                    c_data.Path, thenode.data
                )
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
                    anode_nid = thenode.data.Nesting.ANodes.get(aname, {}).get("Nid")
                    if anode := self.nodes.get(anode_nid):
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
                VFNodeConnectionType.Self: lambda: thenode.data.Connections.Self.keys(),
                VFNodeConnectionType.Attach: lambda: thenode.data.Connections.Attach.keys(),
                VFNodeConnectionType.Inputs: lambda: thenode.data.Connections.Inputs.keys(),
                VFNodeConnectionType.Outputs: lambda: thenode.data.Connections.Outputs.keys(),
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

                return [f"{item.NodeId}/{'/'.join(item.DataPath)}" for item in tmp_vars]

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
        # 构建节点连接关系
        # for edgeinfo in flowdata.edges:
        #     if edgeinfo.source in self.nodes and edgeinfo.target in self.nodes:
        #         source_handle = edgeinfo.sourceHandle
        #         target_handle = edgeinfo.targetHandle
        #         if edgeinfo.source not in self.connectGraph:
        #             self.connectGraph[edgeinfo.source] = {"source": {}, "target": {}}
        #             pass
        #         if source_handle not in self.connectGraph[edgeinfo.source]["source"]:
        #             self.connectGraph[edgeinfo.source]["source"][source_handle] = []
        #             pass
        #         self.connectGraph[edgeinfo.source]["source"][source_handle].append(
        #             {"nid": edgeinfo.target, "hid": target_handle}
        #         )
        #         pass
        #         if edgeinfo.target not in self.connectGraph:
        #             self.connectGraph[edgeinfo.target] = {"source": {}, "target": {}}
        #             pass
        #         if target_handle not in self.connectGraph[edgeinfo.target]["target"]:
        #             self.connectGraph[edgeinfo.target]["target"][target_handle] = []
        #             pass
        #         self.connectGraph[edgeinfo.target]["target"][target_handle].append(
        #             {"nid": edgeinfo.source, "hid": source_handle}
        #         )
        #         pass

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
            # if len(node.validateNeededs) <= 0:
            #     continue
            # validateVarDict: Dict[FANodeValidateNeed, Any] = {}
            # if FANodeValidateNeed.Self in node.validateNeededs:
            #     validateVarDict[FANodeValidateNeed.Self] = [
            #         f"{item.nodeId}/{item.dpath[0]}/{item.dpath[1]}"
            #         for item in self.recursive_find_variables(
            #             nid, ["self"], [], [], False, [], False, []
            #         )
            #     ]
            #     pass
            # if FANodeValidateNeed.AttachOutput in node.validateNeededs:
            #     validateVarDict[FANodeValidateNeed.AttachOutput] = [
            #         f"{item.nodeId}/{item.dpath[0]}/{item.dpath[1]}"
            #         for item in self.recursive_find_variables(
            #             nid, ["attach_output"], [], [], False, [], False, []
            #         )
            #     ]
            #     pass
            # if FANodeValidateNeed.InputNodes in node.validateNeededs:
            #     validateVarDict[FANodeValidateNeed.InputNodes] = {
            #         inhid: [
            #             f"{item['nid']}/{item['hid']}"
            #             for item in self.get_handle_connections(nid, "target", inhid)
            #         ]
            #         for inhid in node.data.connections.inputs.keys()
            #     }
            # if FANodeValidateNeed.InputNodesWVars in node.validateNeededs:
            #     validateVarDict[FANodeValidateNeed.InputNodesWVars] = {
            #         inhid: {
            #             item["nid"]: {
            #                 item["hid"]: [
            #                     f"{item2.nodeId}/{item2.dpath[0]}/{item2.dpath[1]}"
            #                     for item2 in self.recursive_find_variables(
            #                         item["nid"],
            #                         [],
            #                         [],
            #                         [],
            #                         False,
            #                         [],
            #                         False,
            #                         [item["hid"]],
            #                     )
            #                 ]
            #             }
            #             for item in self.get_handle_connections(nid, "target", inhid)
            #         }
            #         for inhid in node.data.connections.inputs.keys()
            #     }
            #     pass
            validation = await node.validate(self)
            if validation:
                validations.append(validation)
        pass
        return validations
