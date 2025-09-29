from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "User_"

    UserId = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    Utilisateur = Column(String(20), nullable=False)
    UidHex = Column(String(32), unique=True, nullable=False)
    role = Column(Integer, nullable=False)
    CreatedAt = Column(DateTime, server_default=func.now(), nullable=False)
