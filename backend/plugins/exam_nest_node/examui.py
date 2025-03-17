from app.uisdk import *


class ExamUI(NInput):
    def __init__(self):
        super().__init__(
            type="info",
            value=PropVar(
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
        )


EXPORT_UI = ExamUI