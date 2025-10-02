import mysql.connector

try:
    # Connexion MySQL
    conn = mysql.connector.connect(
        host="localhost",
        user="root",          # ou "ievan"
        password="uimm",      # ou "mdp_1234"
        database="NEE_Electronic",
        port=3306
    )

    if conn.is_connected():
        print("✅ Connexion réussie à la base MySQL")

        cursor = conn.cursor()

        # Récupérer toutes les tables
        cursor.execute("SHOW TABLES;")
        tables = [t[0] for t in cursor.fetchall()]
        print("📂 Tables :", tables)

        # Pour chaque table → afficher toutes les données
        for table in tables:
            print(f"\n--- Contenu de {table} ---")
            cursor.execute(f"SELECT * FROM {table};")
            rows = cursor.fetchall()
            for row in rows:
                print(row)

except mysql.connector.Error as err:
    print(f"❌ Erreur MySQL : {err}")

finally:
    if 'conn' in locals() and conn.is_connected():
        conn.close()
        print("\n🔒 Connexion fermée")
