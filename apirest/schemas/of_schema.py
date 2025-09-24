from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

class OFBase(BaseModel) : 
  """Schéma de base pour un OF"""
    name: str = Field(..., description="Nom de l'ordre de fabrication", max_length=50)
    product_name: str = Field(..., description="Nom du produit à fabriquer", max_length=100)
    quantity: float = Field(..., gt=0, description="Quantité à produire")
    state: str = Field(..., description="État de l'OF")