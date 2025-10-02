# schemas/user.py
from pydantic import BaseModel

class TagRequest(BaseModel):
    badgeID: str

class TagResponse(BaseModel):
    badgeID: str
    role: int