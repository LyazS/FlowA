from app.uisdk import *


class ExamUI(NInput):
    def __init__(self):
        super().__init__(
            type="info",
            value="Hello World",
            size="small",
            clearable=True,
        )


EXPORT_UI = ExamUI
