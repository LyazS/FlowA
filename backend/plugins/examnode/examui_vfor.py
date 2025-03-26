from app.uisdk import *


class ExamUI_vfor(ForLoopComponent):
    def __init__(self):
        super().__init__(
            Items=ValueProp(Data=[1, 2, 3, 4, 5]),
            ItemLabel="@ExamItem",
            IndexLabel="@ExamIndex",
            Template=NFlex(
                align="center",
                justify="center",
                vertical=False,
                wrap=False,
                slots={
                    "default": [
                        SpanComponent(
                            Type=PropVarType.VBind, Data=[VFOR_DATA, "@ExamItem"]
                        ),
                        SpanComponent(
                            Type=PropVarType.VBind, Data=[VFOR_DATA, "@ExamIndex"]
                        ),
                    ]
                },
            ),
        )


EXPORT_UI = ExamUI_vfor
