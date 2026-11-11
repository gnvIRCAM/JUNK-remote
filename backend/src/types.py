from pydantic import BaseModel
import typing as tp


AppPages = tp.Literal["menu", "patch"]

class KnobKind(BaseModel):
    index: int
    value: float