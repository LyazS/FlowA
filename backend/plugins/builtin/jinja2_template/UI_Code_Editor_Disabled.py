from ..UI_Components.UI_CodeEditor import UI_CodeEditor


class UI_Code_Editor_Disabled(UI_CodeEditor):
    def __init__(self):
        super().__init__(useDisabled=False)

    pass


EXPORT_UI = UI_Code_Editor_Disabled
