import logging
import time
import os
import re
from logging.handlers import TimedRotatingFileHandler
import mysql.connector
from typing import Optional
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def clean_message(msg: str) -> str:
    return re.sub(r"[^a-zA-Z0-9 .,;:!?@#&()_\-\[\]{}]", "", msg)

class MySQLHandler(logging.Handler):
    def __init__(self, host, user, password, database, port=3306, table="logs"):
        super().__init__()
        host = os.getenv("MYSQL_HOST", "localhost")
        port = int(os.getenv("MYSQL_PORT", 3306))
        user = os.getenv("MYSQL_USER")
        password = os.getenv("MYSQL_PASSWORD")
        database = os.getenv("MYSQL_DATABASE")

        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port          # <-- ajout du port ici
        )
        self.cursor = self.conn.cursor()
        self.cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table} (
                id INT AUTO_INCREMENT PRIMARY KEY,
                timestamp VARCHAR(32),
                level VARCHAR(10),
                logger VARCHAR(50),
                message TEXT
            )
        """)
        self.conn.commit()
        self.table = table

    def emit(self, record):
        try:
            message = clean_message(record.getMessage())
            self.cursor.execute(
                f"INSERT INTO {self.table} (timestamp, level, logger, message) VALUES (%s, %s, %s, %s)",
                (self.formatTime(record), record.levelname, record.name, message)
            )
            self.conn.commit()
        except Exception as e:
            print(f"[LOGGING][MySQL] Erreur d'insertion: {e}")

def setup_logging(name: str, level: int = logging.INFO, logfile: Optional[str] = None, use_mysql: bool = True):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.handlers:
        return logger

    logging.Formatter.converter = time.gmtime
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    ch.setLevel(level)
    logger.addHandler(ch)

    if logfile:
        os.makedirs(os.path.dirname(logfile), exist_ok=True)
        fh = TimedRotatingFileHandler(logfile, when="midnight", interval=30, backupCount=12, encoding="utf-8")
        fh.setFormatter(fmt)
        fh.setLevel(level)
        logger.addHandler(fh)

    if use_mysql:
        try:
            db_handler = MySQLHandler()
            db_handler.setFormatter(fmt)
            db_handler.setLevel(level)
            logger.addHandler(db_handler)
        except Exception as e:
            print(f"[LOGGING][MySQL] ❌ Connexion MySQL impossible : {e}")

    return logger
