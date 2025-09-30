from pydantic import BaseModel
from typing import Any, List, Optional

class WriteData(BaseModel):
    node_name: str
    value: Any
    variant_type: Optional[str] = None  # ex : "Int16", "Boolean", etc.

class WriteMultipleData(BaseModel):
    writes: List[WriteData]

class ReadResponse(BaseModel):
    node_id: str
    value: Any
    error: Optional[str] = None

class ReadMultipleResponse(BaseModel):
    results: List[ReadResponse]

class WriteRequest(BaseModel):
    node_id: str
    value: Optional[str] = None
    variant_type: Optional[str] = None