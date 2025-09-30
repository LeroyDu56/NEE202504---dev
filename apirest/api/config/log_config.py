import logging
import time
import os
from logging.handlers import TimedRotatingFileHandler
import mysql.connector

# ==========================
# Handler custom pour MySQL
# ==========================
class MySQLHandler(logging.Handler):
    def __init__(self, host, user, password, database, table="logs"):
        super().__init__()
        self.conn = mysql.connector.connect(
            host=host, user=user, password=password, database=database
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
            self.cursor.execute(
                f"INSERT INTO {self.table} (timestamp, level, logger, message) VALUES (%s, %s, %s, %s)",
                (self.formatTime(record), record.levelname, record.name, record.getMessage())
            )
            self.conn.commit()
        except Exception as e:
            print(f"[LOGGING][MySQL] Erreur d'insertion: {e}")

# ==========================
# Setup logging par service
# ==========================
def setup_logging(
    name: str,
    level: int = logging.INFO,
    logfile: str | None = None,
    mysql_conf: dict | None = None,
):
    """
    Configure un logger par service :
    - Console
    - Fichier mensuel rotatif (si logfile fourni)
    - Base MySQL (optionnelle)
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.handlers:  # éviter doublons
        return logger

    # UTC + format simple
    logging.Formatter.converter = time.gmtime
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    # --- Console ---
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    ch.setLevel(level)
    logger.addHandler(ch)

    # --- Fichier par service ---
    if logfile:
        os.makedirs(os.path.dirname(logfile), exist_ok=True)
        fh = TimedRotatingFileHandler(
            logfile,
            when="midnight",
            interval=30,      # rotation mensuelle
            backupCount=12,   # garde 12 mois d'historique
            encoding="utf-8"
        )
        fh.setFormatter(fmt)
        fh.setLevel(level)
        logger.addHandler(fh)

    # --- MySQL ---
    if mysql_conf:
        db_handler = MySQLHandler(**mysql_conf)
        db_handler.setFormatter(fmt)
        db_handler.setLevel(level)
        logger.addHandler(db_handler)

    return logger
