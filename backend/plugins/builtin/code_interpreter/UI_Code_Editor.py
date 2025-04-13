from ..UI_Components.UI_CodeEditor import UI_CodeEditor


class UI_Code_Editor(UI_CodeEditor):
    def __init__(self):
        super().__init__(useDisabled=None)

    pass


EXPORT_UI = UI_Code_Editor
