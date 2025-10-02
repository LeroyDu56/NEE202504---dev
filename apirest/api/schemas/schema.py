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


class OF(BaseModel):
    name: str
    product_id: List  # [id, nom produit]
    product_qty: int
    qty_produced: int
    state: str
    date_planned_start: Optional[str]
    date_planned_finished: Optional[str]
    bom_ref: Optional[str] 
