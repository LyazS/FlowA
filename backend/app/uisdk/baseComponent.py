from typing import List, Dict
from pydantic import BaseModel


class BaseComponent(BaseModel):
    Type: str
    Props: Dict
    Slots: List
    pass
