from typing import Optional, Dict, List, Union, Literal
from app.uisdk import *
from app.schemas.VFNodeInterface import VarType
from .NFlex import NFlex
from .NInput import NInput
from .NButton import NButton
from .Header import Header
from .RefVarSelect import UI_RefVarSelect


class UI_FileUpload(NFlex):
    def __init__(
        self,
        value: List[str | int],
        fileType: UploadFileInfoType,
        filterType: Optional[List[str]] = None,
        width: Optional[str | PropVar] = None,
        size: PropVar | Literal["tiny", "small", "medium", "large"] = "medium",
        style: Optional[Dict] = {},
        IfCondition: Optional[Condition] = None,
    ):
        super().__init__(
            vertical=False,
            wrap=False,
            justify="space-between",
            style={
                "align-content": "center",
                "align-items": "center",
                "width": width,
                **style,
            },
            IfCondition=IfCondition,
            slots={
                "default": [
                    NormalComponent(
                        Type="NEllipsis",
                        Props={
                            "style": {"width": "60%", "max-width": "60%"},
                        },
                        Slots={"default": SpanComponent(VBindProp(value + ["Name"]))},
                    ),
                    NButton(
                        type="warning",
                        size=size,
                        level="tertiary",
                        style={"width": "40%"},
                        onClick=OperateFunctionProp(
                            [
                                SETITEM_FuncProp(
                                    Arg=FuncArg_SETITEM(
                                        DstPath=VBindProp(value),
                                        ItemValue=AsyncReturnFunctionProp(
                                            UPLOADFILE_FuncProp(
                                                Arg=FuncArg_UPLOADFILE(
                                                    FileType=fileType,
                                                    FilterType=filterType,
                                                )
                                            )
                                        ),
                                    )
                                )
                            ]
                        ),
                        slots={
                            "default": SpanComponent(ValueProp("上传")),
                            "icon": NormalComponent(Type="CloudUploadOutline"),
                        },
                    ),
                ]
            },
        )
