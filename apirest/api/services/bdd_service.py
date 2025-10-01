from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError
from apirest.api.models.user_model import Base, User
import logging
from typing import Optional
import os
from dotenv import load_dotenv

logger = logging.getLogger("BDD")

load_dotenv()

class Database:
    def __init__(self):
        db_url = (
            f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}"
            f"@{os.getenv('MYSQL_HOST', 'localhost')}:{os.getenv('MYSQL_PORT', '3306')}/{os.getenv('MYSQL_DATABASE')}"
        )
        self.engine = create_engine(db_url, pool_pre_ping=True)
        self.Session = sessionmaker(bind=self.engine, autocommit=False, autoflush=False)
        Base.metadata.create_all(bind=self.engine)

    def get_session(self) -> Session:
        return self.Session()

    def check_connection(self) -> bool:
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except OperationalError as e:
            logger.error(f"Erreur de connexion : {e}")
            return False

    def get_role_by_tag(self, session: Session, uid_hex: str) -> Optional[int]:
        user = session.query(User).filter(User.UidHex == uid_hex).first()
        return user.role if user else None
