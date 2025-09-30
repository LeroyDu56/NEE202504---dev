# schemas/user.py
from pydantic import BaseModel

class TagRequest(BaseModel):
    tag_rfid: str

class TagResponse(BaseModel):
    tag_rfid: str
    role: int