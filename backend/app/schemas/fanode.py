from typing import List, Optional, Any
from pydantic import BaseModel
from enum import StrEnum


class FARunStatus(StrEnum):
    Default = "Default"
    Pending = "Pending"
    Running = "Running"
    Success = "Success"
    Canceled = "Canceled"
    Error = "Error"
    Passive = "Passive"
    pass


class FANodeWaitType(StrEnum):
    AND = "AND"
    OR = "OR"
    pass


class FANodeValidateNeed(StrEnum):
    Self = "Self"
    AttachOutput = "AttachOutput"
    InputNodes = "InputNodes"
    InputNodesWVars = "InputNodesWVars"
    pass
