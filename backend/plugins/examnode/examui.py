from app.uisdk import *


class ExamUI(NInput):
    def __init__(self):
        super().__init__(
            type="textarea",
            value=VModelProp(
                Type=PropVarType.VModel,
                Data=[
                    THIS_NODE_DATA,
                    "Payloads",
                    "ById",
                    PAYLOADS_ID,
                    "Data",
                ],
            ),
            size="small",
            clearable=True,
            showCount=True,
            autosize=NInputAutoSize(minRows=3, maxRows=5),
        )


EXPORT_UI = ExamUI
