from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, date

class OFBase(BaseModel) : 
  """Schéma de base pour un OF"""
    id: int
    name: str
    product_id: List[int]  # Format retourné par Odoo : [id, name]
    product_name: str
    product_qty: float
    qty_produced: float
    state: str
    date_planned_start: Optional[date] = None
    date_planned_finished: Optional[date] = None
    progress_percent: float
