from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.exc import OperationalError
import os
from dotenv import load_dotenv
from api.models.user_model import Base, User

load_dotenv()  # Charge les variables d'environnement

class Database:
    def __init__(self):
        db_url = (
            f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}"
            f"@{os.getenv('MYSQL_HOST', 'localhost')}:3306/{os.getenv('MYSQL_DATABASE')}"
        )
        self.engine = create_engine(db_url, pool_pre_ping=True)
        self.Session = sessionmaker(bind=self.engine, autocommit=False, autoflush=False)

        # Création des tables si elles n'existent pas
        Base.metadata.create_all(bind=self.engine)

    def get_session(self) -> Session:
        """Retourne une nouvelle session SQLAlchemy."""
        return self.Session()

    def check_connection(self) -> bool:
        """Teste si la connexion à la BDD est active."""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except OperationalError as e:
            print(f"Erreur de connexion : {e}")
            return False

    def get_role_by_tag(self, session: Session, uid_hex: str) -> int | None:
        """Récupère le rôle associé à un tag RFID (UidHex)."""
        user = session.query(User).filter(User.UidHex == uid_hex).first()
        return user.role if user else 0