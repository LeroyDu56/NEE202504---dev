from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, date

# Modèle pour le JSON d'entrée
class OFData(BaseModel):
    OF: int
    Recette: int
    Quantite: int