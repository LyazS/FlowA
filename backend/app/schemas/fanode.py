from typing import List, Optional, Any
from pydantic import BaseModel
from enum import Enum


class FARunStatus(Enum):
    Default = "Default"
    Pending = "Pending"
    Running = "Running"
    Success = "Success"
    Canceled = "Canceled"
    Error = "Error"
    Passive = "Passive"
    pass


class FANodeWaitType(Enum):
    AND = "AND"
    OR = "OR"
    pass


class FANodeValidateNeed(Enum):
    Self = "Self"
    AttachOutput = "AttachOutput"
    InputNodes = "InputNodes"
    InputNodesWVars = "InputNodesWVars"
    pass
