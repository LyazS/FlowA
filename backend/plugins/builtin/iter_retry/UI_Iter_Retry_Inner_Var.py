from app.uisdk import *
from ..UI_Components.UI_Inner_Var_Tag import UI_Inner_Var_Tag, TagPath


class UI_Iter_Retry_Inner_Var(UI_Inner_Var_Tag):
    def __init__(self):
        super().__init__(
            [
                TagPath(
                    label_path=[
                        THIS_NODE_DATA,
                        "Payloads",
                        "ById",
                        "D_ITER_ITEM",
                        "Label",
                    ],
                    type_path=[
                        THIS_NODE_DATA,
                        "Payloads",
                        "ById",
                        "D_ITER_ITEM",
                        "Type",
                    ],
                ),
                TagPath(
                    label_path=[
                        THIS_NODE_DATA,
                        "Payloads",
                        "ById",
                        "D_ITER_INDEX",
                        "Label",
                    ],
                    type_path=[
                        THIS_NODE_DATA,
                        "Payloads",
                        "ById",
                        "D_ITER_INDEX",
                        "Type",
                    ],
                ),
            ]
        )

        pass


EXPORT_UI = UI_Iter_Retry_Inner_Var
