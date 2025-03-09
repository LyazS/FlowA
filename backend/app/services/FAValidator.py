from typing import Dict, List, Optional, Any
from app.schemas.farequest import VarItem, ValidationError
from app.schemas.vfnode import (
    VFNodeConnectionDataType,
    VFlowData,
    VFNodeConnectionDataAttachedType,
)
from app.schemas.fanode import FANodeValidateNeed
from app.nodes import FATaskNode, FANODECOLLECTION


class FAValidator:
    def __init__(self):
        self.nodes: Dict[str, FATaskNode] = {}
        self.connectGraph = {}
        pass

    def get_handle_connections(self, nid, type, hid):
        if nid in self.connectGraph:
            if type == "source" and hid in self.connectGraph[nid]["source"]:
                return self.connectGraph[nid]["source"][hid]
            elif type == "target" and hid in self.connectGraph[nid]["target"]:
                return self.connectGraph[nid]["target"][hid]
        return []

    def recursive_find_variables(
        self,
        nid: str,
        find_self: List[str] = [],
        find_attach: List[str] = [],
        find_next: List[str] = [],
        find_all_input: bool = False,
        find_input: List[str] = None,
        find_all_output: bool = False,
        find_output: List[str] = None,
    ) -> List[VarItem]:
        if find_input is None:
            find_input = []
        if find_output is None:
            find_output = []

        result = []
        the_node = self.nodes[nid]

        if find_all_input:
            find_input = list(the_node.data.connections.inputs.keys())
        if find_all_output:
            find_output = list(the_node.data.connections.outputs.keys())

        for hid in find_self:
            result.extend(self.find_var_from_io(nid, "self", hid))
        for hid in find_attach:
            result.extend(self.find_var_from_io(nid, "attach", hid))
        for hid in find_next:
            result.extend(self.find_var_from_io(nid, "next", hid))
        for hid in find_input:
            result.extend(self.find_var_from_io(nid, "inputs", hid))
        for hid in find_output:
            result.extend(self.find_var_from_io(nid, "outputs", hid))

        return result

    def find_var_from_io(
        self,
        nid: str,
        findconnect: str,
        hid: str,
    ) -> List[VarItem]:
        result = []
        thenode = self.nodes[nid]  # 假设这个函数在其他地方定义

        # 根据类型获取connection数据
        if (
            findconnect == "self"
            and thenode.data.connections.self != None
            and hid in thenode.data.connections.self
        ):
            connection = thenode.data.connections.self[hid].data
        elif (
            findconnect == "attach"
            and thenode.data.connections.attach != None
            and hid in thenode.data.connections.attach
        ):
            connection = thenode.data.connections.attach[hid].data
        elif (
            findconnect == "next"
            and thenode.data.connections.next != None
            and hid in thenode.data.connections.next
        ):
            connection = thenode.data.connections.next[hid].data
        elif (
            findconnect == "inputs"
            and thenode.data.connections.inputs != None
            and hid in thenode.data.connections.inputs
        ):
            connection = thenode.data.connections.inputs[hid].data
        elif (
            findconnect == "outputs"
            and thenode.data.connections.outputs != None
            and hid in thenode.data.connections.outputs
        ):
            connection = thenode.data.connections.outputs[hid].data
        else:
            return result

        for c_data in connection.values():
            if c_data.type == VFNodeConnectionDataType.FromInner:
                result.append(
                    VarItem(
                        nodeId=nid,
                        nlabel=thenode.data.label,
                        dpath=c_data.path,
                        dlabel=thenode.data.getContent(c_data.path[0])
                        .byId[c_data.path[1]]
                        .label,
                        dkey=thenode.data.getContent(c_data.path[0])
                        .byId[c_data.path[1]]
                        .key,
                        dtype=thenode.data.getContent(c_data.path[0])
                        .byId[c_data.path[1]]
                        .type,
                    )
                )

            elif c_data.type == VFNodeConnectionDataType.FromOuter:
                # 对于上一个节点，递归搜索上个节点的对应输出handle
                in_hid = c_data.inputKey
                edges = self.get_handle_connections(nid, "target", in_hid)
                for edge in edges:
                    src_nid = edge["nid"]
                    src_hid = edge["hid"]
                    result.extend(
                        self.recursive_find_variables(
                            src_nid, [], [], [], False, [], False, [src_hid]
                        )
                    )

            elif c_data.type == VFNodeConnectionDataType.FromAttached:
                # 对于子节点的处理
                result.extend(
                    self.recursive_find_variables(
                        thenode.data.nesting.attached_nodes[c_data.atype].nid,
                        (
                            ["self"]
                            if c_data.atype
                            == VFNodeConnectionDataAttachedType.attached_node_output
                            else []
                        ),
                        [],
                        [],
                        False,
                        [],
                        c_data.atype
                        == VFNodeConnectionDataAttachedType.attached_node_input,
                        [],
                    )
                )

            elif c_data.type == VFNodeConnectionDataType.FromParent:
                # 如果是父节点，递归搜索父节点的所有输入handle
                result.extend(
                    self.recursive_find_variables(
                        thenode.parentNode, [], ["attach"], [], True, [], False, []
                    )
                )

        return result

    async def validate(
        self,
        wid: str,
        flowdata: VFlowData,
    ) -> Dict[str, ValidationError]:
        # 初始化所有节点
        for nodeinfo in flowdata.nodes:
            node = (FANODECOLLECTION[nodeinfo.data.ntype])(wid, nodeinfo, None)
            self.nodes[nodeinfo.id] = node
            pass
        # 构建节点连接关系
        for edgeinfo in flowdata.edges:
            if edgeinfo.source in self.nodes and edgeinfo.target in self.nodes:
                source_handle = edgeinfo.sourceHandle
                target_handle = edgeinfo.targetHandle
                if edgeinfo.source not in self.connectGraph:
                    self.connectGraph[edgeinfo.source] = {"source": {}, "target": {}}
                    pass
                if source_handle not in self.connectGraph[edgeinfo.source]["source"]:
                    self.connectGraph[edgeinfo.source]["source"][source_handle] = []
                    pass
                self.connectGraph[edgeinfo.source]["source"][source_handle].append(
                    {"nid": edgeinfo.target, "hid": target_handle}
                )
                pass
                if edgeinfo.target not in self.connectGraph:
                    self.connectGraph[edgeinfo.target] = {"source": {}, "target": {}}
                    pass
                if target_handle not in self.connectGraph[edgeinfo.target]["target"]:
                    self.connectGraph[edgeinfo.target]["target"][target_handle] = []
                    pass
                self.connectGraph[edgeinfo.target]["target"][target_handle].append(
                    {"nid": edgeinfo.source, "hid": source_handle}
                )
                pass
        # 逐个节点验证，主要验证变量是否合法
        validations: List[ValidationError] = []
        for nid in self.nodes.keys():
            node = self.nodes[nid]
            if len(node.validateNeededs) <= 0:
                continue
            validateVarDict: Dict[FANodeValidateNeed, Any] = {}
            if FANodeValidateNeed.Self in node.validateNeededs:
                validateVarDict[FANodeValidateNeed.Self] = [
                    f"{item.nodeId}/{item.dpath[0]}/{item.dpath[1]}"
                    for item in self.recursive_find_variables(
                        nid, ["self"], [], [], False, [], False, []
                    )
                ]
                pass
            if FANodeValidateNeed.AttachOutput in node.validateNeededs:
                validateVarDict[FANodeValidateNeed.AttachOutput] = [
                    f"{item.nodeId}/{item.dpath[0]}/{item.dpath[1]}"
                    for item in self.recursive_find_variables(
                        nid, ["attach_output"], [], [], False, [], False, []
                    )
                ]
                pass
            if FANodeValidateNeed.InputNodes in node.validateNeededs:
                validateVarDict[FANodeValidateNeed.InputNodes] = {
                    inhid: [
                        f"{item['nid']}/{item['hid']}"
                        for item in self.get_handle_connections(nid, "target", inhid)
                    ]
                    for inhid in node.data.connections.inputs.keys()
                }
            if FANodeValidateNeed.InputNodesWVars in node.validateNeededs:
                validateVarDict[FANodeValidateNeed.InputNodesWVars] = {
                    inhid: {
                        item["nid"]: {
                            item["hid"]: [
                                f"{item2.nodeId}/{item2.dpath[0]}/{item2.dpath[1]}"
                                for item2 in self.recursive_find_variables(
                                    item["nid"],
                                    [],
                                    [],
                                    [],
                                    False,
                                    [],
                                    False,
                                    [item["hid"]],
                                )
                            ]
                        }
                        for item in self.get_handle_connections(nid, "target", inhid)
                    }
                    for inhid in node.data.connections.inputs.keys()
                }
                pass
            validation = node.validate(validateVarDict)
            if validation:
                validations.append(validation)
        pass
        return validations
