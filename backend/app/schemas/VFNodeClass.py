from typing import Optional, Union
from app.schemas.VFNodeInterface import *
from app.utils.tools import getUuid


class VFNode(VFNodeData):
    # 初始化方法 ====================================================
    def __init__(self, v_type: str):
        super().__init__(
            NType="",
            VType=v_type,
            Flag=VFNodeFlag.IsNone,
            Label="",
            PlaceholderLabel="",
            Size=VFNodeSize(Width=-1, Height=-1),
            Connections=self._create_default_connections(),
            Payloads=self._create_default_contents(),
            Results=self._create_default_contents(),
            State=self._create_default_state(),
            Config=self._create_default_config(),
        )
        self.MinSize: Optional[VFNodeSize] = None
        self.Attaching: Optional[VFNodeAttaching] = None
        self.Nesting: Optional[VFNodeNesting] = None

    def model_dump(self, **kwargs) -> dict:
        """生成排除State字段的字典"""
        return super().model_dump(exclude={"State"}, **kwargs)

    def model_dump_json(self, **kwargs) -> str:
        """生成排除State字段的JSON字符串"""
        return super().model_dump_json(exclude={"State"}, **kwargs)

    def _create_default_connections(self) -> VFNodeConnections:
        return VFNodeConnections(
            Self={},
            Attach={},
            Inputs={},
            Outputs={},
            CallbackUsers={},
            CallbackFuncs={},
        )

    def _create_default_contents(self) -> VFNodeContents:
        return VFNodeContents(ById={}, Order=[])

    def _create_default_state(self) -> VFNodeState:
        return VFNodeState(
            Status="Default",
            Copy={},
            CopyCount={"Running": 0, "Success": 0, "Error": 0},
            Errors=[],
        )

    def _create_default_config(self) -> VFNodeConfig:
        return VFNodeConfig(OutputsUiType="")

    # 类型初始化方法 ================================================
    def init_as_nested_node(
        self,
        tag: Optional[str],
        minsize=VFNodeSize(Width=200, Height=200),
        pad=VFNodePadding(Top=60, Bottom=40, Left=60, Right=60, Gap=0),
        apad=VFNodePadding(Top=30, Bottom=25, Left=17, Right=17, Gap=20),
    ) -> "VFNode":
        self.MinSize = minsize
        self.Nesting = VFNodeNesting(
            Tag=tag,
            Pad=pad,
            APad=apad,
            ANodes={},
        )
        self.Flag |= VFNodeFlag.IsNested
        return self

    def init_as_attached_node(
        self, a_type: VFNodeAttachingType, pos: VFNodeAttachingPos, label: str
    ) -> "VFNode":
        self.Attaching = VFNodeAttaching(Type=a_type, Pos=pos, Label=label)
        self.Flag |= VFNodeFlag.IsAttached
        return self

    # 类型守卫 ======================================================
    @property
    def is_attached_node(self) -> bool:
        return (self.Flag & VFNodeFlag.IsAttached) != 0

    @property
    def is_nested_node(self) -> bool:
        return (self.Flag & VFNodeFlag.IsNested) != 0

    # 属性操作方法 ==================================================
    def getContent(
        self,
        content_name: Literal["Payloads", "Results"],
    ) -> Union[VFNodeContents, None]:
        if content_name == "Payloads":
            return self.Payloads
        elif content_name == "Results":
            return self.Results
        else:
            return None
        pass

    def set_node_type(self, n_type: str) -> "VFNode":
        self.NType = n_type
        return self

    def set_label(self, label: str) -> "VFNode":
        self.Label = label
        self.PlaceholderLabel = label
        return self

    def set_size(self, width: int, height: int) -> "VFNode":
        min_width = self.MinSize.Width if self.MinSize else 0
        min_height = self.MinSize.Height if self.MinSize else 0
        self.Size = VFNodeSize(
            Width=max(width, min_width), Height=max(height, min_height)
        )
        return self

    def set_flag(self, flag: int) -> "VFNode":
        self.Flag = flag
        return self

    def add_flag(self, flag: int) -> "VFNode":
        self.Flag |= flag
        return self

    def rm_flag(self, flag: int) -> "VFNode":
        self.Flag &= ~flag
        return self

    def set_outputs_ui_type(self, ui_type: str) -> "VFNode":
        self.Config.OutputsUiType = ui_type
        return self

    # 连接点操作 ====================================================
    def add_handle(
        self,
        connect_type: VFNodeConnectionType,
        handle_id: str,
        label: Optional[str] = None,
    ) -> "VFNode":
        getattr(self.Connections, connect_type.value)[handle_id] = VFNodeHandle(
            Label=label or handle_id, Data={}
        )
        return self

    def add_handle_data(
        self,
        connect_type: VFNodeConnectionType,
        handle_id: str,
        data: VFNodeHandleData,
        data_id: Optional[str] = None,
    ) -> str:
        handle: VFNodeHandle = getattr(self.Connections, connect_type.value).get(
            handle_id
        )
        if not handle:
            raise ValueError(f"Handle {handle_id} not found in {connect_type}")

        did = data_id or getUuid()
        handle.Data[did] = data
        return did

    def remove_handle(
        self, connect_type: VFNodeConnectionType, handle_id: str
    ) -> "VFNode":
        connection = getattr(self.Connections, connect_type.value)
        if handle_id in connection:
            del connection[handle_id]
        return self

    def remove_handle_data(
        self, connect_type: VFNodeConnectionType, handle_id: str, data_id: str
    ) -> "VFNode":
        handle: VFNodeHandle = getattr(self.Connections, connect_type.value).get(
            handle_id
        )
        if handle and data_id in handle.Data:
            del handle.Data[data_id]
        return self

    # 数据内容操作 ==================================================
    def add_result_into_outputs(
        self,
        content: VFNodeContentData,
        handle_id: str,
        result_id: Optional[str] = None,
        data_id: Optional[str] = None,
    ) -> str:
        if handle_id not in self.Connections.Outputs:
            self.add_handle(VFNodeConnectionType.Outputs, handle_id)

        rid = result_id or getUuid()
        did = self.add_handle_data(
            VFNodeConnectionType.Outputs,
            handle_id,
            VFNodeHandleData(
                Type=VFNodeConnectionDataType.FromInner,
                Path=FromInnerPath(ContentName="Results", ContentId=rid),
                UseIds=[],
            ),
            data_id,
        )

        self.Results.ById[rid] = content.model_copy(
            update={"Hid": handle_id, "Did": did},
            deep=True,
        )
        self.Results.Order.append(rid)
        return rid

    def remove_result_into_outputs(self, result_id: str) -> "VFNode":
        result = self.Results.ById.get(result_id)
        if not result:
            return self

        handle_id = result.Hid
        data_id = result.Did
        if handle_id and data_id:
            self.remove_handle_data(VFNodeConnectionType.Outputs, handle_id, data_id)

        if result_id in self.Results.ById:
            del self.Results.ById[result_id]
        if result_id in self.Results.Order:
            self.Results.Order.remove(result_id)
        return self

    # 数据内容操作补充 ==============================================
    def add_payload(
        self, content: VFNodeContentData, payload_id: Optional[str] = None
    ) -> str:
        pid = payload_id or getUuid()
        self.Payloads.ById[pid] = content.model_copy(
            update={"Hid": "", "Did": ""},
            deep=True,
        )
        self.Payloads.Order.append(pid)
        return pid

    def remove_payload(self, payload_id: str) -> "VFNode":
        if payload_id in self.Payloads.ById:
            del self.Payloads.ById[payload_id]
            self.Payloads.Order.remove(payload_id)
        return self

    def add_result(
        self, content: VFNodeContentData, result_id: Optional[str] = None
    ) -> str:
        rid = result_id or getUuid()
        self.Results.ById[rid] = content.model_copy(
            update={"Hid": "", "Did": ""},
            deep=True,
        )
        self.Results.Order.append(rid)
        return rid

    def remove_result(self, result_id: str) -> "VFNode":
        if result_id in self.Results.ById:
            del self.Results.ById[result_id]
            self.Results.Order.remove(result_id)
        return self

    # 状态管理 ======================================================
    def update_status(self, status: Literal["Running", "Success", "Error"]) -> "VFNode":
        self.State.Status = status
        self.State.CopyCount[status] += 1
        return self

    def reset_state(self) -> "VFNode":
        self.State = self._create_default_state()
        return self

    # 嵌套节点操作补充 ==============================================
    def add_attached_node(
        self,
        a_name: str,
        a_ntype: str,
        # a_type: VFNodeAttachingType,
        # a_pos: VFNodeAttachingPos,
        # a_label: str,
    ) -> "VFNode":
        if not self.is_nested_node:
            raise ValueError("Cannot add attached node to non-nested node")

        self.Nesting.ANodes[a_name] = VFNodeAttachedNode(
            NId=None,
            NType=a_ntype,
            # Type=a_type,
            # Pos=a_pos,
            # Label=a_label,
        )
        return self


# 辅助函数 ========================================================
def create_vf_node_from_data(
    data: VFNodeData,
) -> VFNode:
    node = VFNode(data.VType)
    node.set_node_type(data.NType)
    node.set_label(data.Label)

    # 使用反射设置属性
    for field in data.model_fields_set:
        if field == "State":
            continue
        setattr(node, field, getattr(data, field))

    # 初始化空白状态
    node.State = node._create_default_state()

    return node
