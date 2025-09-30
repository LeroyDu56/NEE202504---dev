import os
import time
from typing import Dict, List
from services.odoo_service import Odoo
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def test_odoo_connection():
    """Test complet de la connexion et récupération des ordres de fabrication depuis Odoo."""

    print("DEBUT DU TEST ODOO")
    print("=" * 60)

    # Configuration depuis variables d'environnement ou valeurs par défaut
    odoo_config = {
        'url': os.getenv('ODOO_URL', 'http://localhost:8069'),
        'database': os.getenv('ODOO_DB', 'your_database'),
        'username': os.getenv('ODOO_USER', 'admin'),
        'password': os.getenv('ODOO_PASSWORD', 'admin')
    }

    print("Configuration utilisée:")
    for key, value in odoo_config.items():
        # Masquer le mot de passe dans l'affichage
        display_value = '*' * len(value) if key == 'password' else value
        print(f"   {key}: {display_value}")

    print("\n" + "-" * 60)

    # Création de l'objet Odoo
    print("CREATION DE L'OBJET Odoo")
    odoo = Odoo(**odoo_config)
    print("Objet Odoo créé")

    print("\n" + "-" * 60)

    # Test de connexion
    print("TEST DE CONNEXION")
    if odoo.connect():
        print("Connexion Odoo réussie !")

        print("\n" + "-" * 60)

        # Test récupération des ordres de fabrication
        print("RECUPERATION DES ORDRES DE FABRICATION")
        start_time = time.time()
        orders = odoo.get_ofs()
        end_time = time.time()

        print(f"Temps de récupération: {end_time - start_time:.2f} secondes")

        if orders:
            print(f"\nRESUME DES ORDRES DE FABRICATION RECUPERES:")
            print(f"   Nombre total: {len(orders)}")

            # Statistiques par état
            states_count = {}
            for order in orders:
                state = order.get('state', 'inconnu')
                states_count[state] = states_count.get(state, 0) + 1

            print(f"   Répartition par état:")
            for state, count in states_count.items():
                print(f"     - {state}: {count}")

            # Affichage détaillé des 5 premiers ordres
            print(f"\nDETAIL DES 5 PREMIERS ORDRES DE FABRICATION:")
            for i, order in enumerate(orders[:5], 1):
                print(f"   {i}. {order.get('name', 'N/A')}")
                product_name = order.get('product_id', ['N/A', 'N/A'])[1] if isinstance(order.get('product_id'), list) else 'N/A'
                print(f"      Produit: {product_name}")
                print(f"      Quantité à produire: {order.get('product_qty', 'N/A')}")
                print(f"      Quantité produite: {order.get('qty_produced', 'N/A')}")
                print(f"      État: {order.get('state', 'N/A')}")
                print(f"      Date de début planifiée: {order.get('date_planned_start', 'N/A')}")
                print(f"      Date de fin planifiée: {order.get('date_planned_finished', 'N/A')}")
                print(f"      ID Odoo: {order.get('id', 'N/A')}")
                print()

            if len(orders) > 5:
                print(f"   ... et {len(orders) - 5} autres ordres de fabrication")

        else:
            print("Aucun ordre de fabrication récupéré")
            print("   Causes possibles:")
            print("   - Aucun ordre de fabrication dans la base Odoo")
            print("   - Problème de droits d'accès")
            print("   - Module Manufacturing non installé")

    else:
        print("Test de connexion échoué")
        print("\nDIAGNOSTIC:")
        print("   1. Vérifiez que le serveur Odoo est démarré")
        print("   2. Vérifiez l'URL (ex: http://localhost:8069)")
        print("   3. Vérifiez le nom de la base de données")
        print("   4. Vérifiez les identifiants (username/password)")
        print("   5. Vérifiez que l'utilisateur a accès au module Manufacturing")

    print("\n" + "-" * 60)

    # Fermeture de la connexion
    print("FERMETURE DE LA CONNEXION")
    odoo.disconnect()

    print("\n" + "=" * 60)
    print("FIN DU TEST")

if __name__ == "__main__":
    test_odoo_connection()
