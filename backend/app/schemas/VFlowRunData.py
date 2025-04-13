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


class VFNodeCacheKeyBefore(StrEnum):
    Skip = "Skip"
    Load = "Load"
    pass


class VFNodeCacheKeyAfter(StrEnum):
    Skip = "Skip"
    Save = "Save"
    pass


class VFNodeCacheKey(BaseModel):
    Before: VFNodeCacheKeyBefore = VFNodeCacheKeyBefore.Load
    Key: Optional[str] = None
    After: VFNodeCacheKeyAfter = VFNodeCacheKeyAfter.Save
    pass
