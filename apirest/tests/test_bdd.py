from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv
import os

# Import des modèles SQLAlchemy
from api.models.user_model import Base, User  

load_dotenv()  # Charge les variables d'environnement depuis .env

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

    def get_role_by_tag(self, session: Session, uid_hex: str) -> str | None:
        """Récupère le rôle associé à un tag RFID (UidHex)."""
        user = session.query(User).filter(User.UidHex == uid_hex).first()
        return user.role if user else 0

    def list_users(self, session: Session):
        """Affiche tous les utilisateurs dans la console."""
        users = session.query(User).all()
        if not users:
            print("❌ Aucun utilisateur dans la base de données.")
            return
        print("📋 Liste des utilisateurs :")
        for u in users:
            # Respecte la casse définie dans le modèle
            print(f"UserId: {u.UserId}, UidHex: {u.UidHex}, Role: {u.role}, CreatedAt: {u.CreatedAt}")


if __name__ == "__main__":
    db = Database()

    # Test connexion
    print("🔄 Test de connexion à MySQL...")
    if db.check_connection():
        print("✅ Connexion réussie à MySQL !")
    else:
        print("❌ Impossible de se connecter à MySQL.")
        exit(1)

    session = db.get_session()
    try:
        # Affiche tous les utilisateurs
        db.list_users(session)

        # Test récupération rôle par tag RFID
        tag_rfid = "2628287182D"  # <-- remplace par un tag existant
        role = db.get_role_by_tag(session, tag_rfid)
        if role:
            print(f"✅ Rôle trouvé pour le tag {tag_rfid} : {role}")
        else:
            print(f"❌ Aucun utilisateur trouvé avec le tag {tag_rfid}")
            print(f"{role}")
    finally:
        session.close()
