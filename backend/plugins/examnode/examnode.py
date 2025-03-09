from typing import List, Dict, Optional, TYPE_CHECKING, Any
from app.schemas.VFNodeClass import VFNode
from app.schemas.vfnode import VFNodeInfo
from app.nodes.basenode import FABaseNode

if TYPE_CHECKING:
    from app.services.FARunner import FARunner


class ExamNode(FABaseNode):
    def __init__(self, wid: str, nodeinfo: VFNodeInfo, runner: "FARunner"):
        super().__init__(wid, nodeinfo, runner)
        pass
