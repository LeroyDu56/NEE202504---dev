import httpx

URL = "http://127.0.0.1:8000/api/opcua/write-of"

# Payload test
payload = {
    "OF": 1,
    "Recette": 31,
    "Quantite": 100
}

def run_test(test_name: str):
    print(f"\n=== Test: {test_name} ===")
    try:
        response = httpx.post(URL, json=payload)
        print("➡️ Requête envoyée :", payload)
        print("⬅️ Statut :", response.status_code)
        try:
            print("⬅️ Réponse :", response.json())
        except Exception:
            print("⬅️ Réponse brute :", response.text)
    except Exception as e:
        print("❌ Erreur lors de l'appel :", e)

if __name__ == "__main__":
    # 1️⃣ Test avec AutWriteOF = False (doit bloquer)
    print("⚠️ Assure-toi que AutWriteOF = False sur le serveur OPC UA")
    run_test("AutWriteOF = False")

    # 2️⃣ Test avec AutWriteOF = True (doit réussir)
    print("\n⚠️ Assure-toi que AutWriteOF = True sur le serveur OPC UA")
    run_test("AutWriteOF = True")
