import sqlite3
import random
from datetime import datetime, timedelta
from pathlib import Path

db_path = Path(__file__).parent.parent / 'data' / 'ventes_2024.db'

# Données de test
categories = [
    ("Électronique", "Appareils électroniques"),
    ("Alimentation", "Produits alimentaires")
]

promotions = [
    ("Soldes Hiver", 20.0, "2024-01-10", "2024-02-10"),
    ("Spécial Été", 15.0, "2024-06-01", "2024-06-30")
]

def peupler_db():
    try:
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        
        # Insertion des catégories
        cur.executemany("INSERT INTO categories (nom, description) VALUES (?, ?)", categories)
        
        # Insertion des promotions
        cur.executemany("""INSERT INTO promotions (nom, remise, date_debut, date_fin)
                        VALUES (?, ?, ?, ?)""", promotions)
        
        # Peuplement des produits (20 exemples)
        produits = []
        for i in range(1, 21):
            produits.append((
                f"Produit {i}",
                random.randint(1, len(categories)),
                round(random.uniform(10, 500), 2),
                random.randint(0, 100),
                random.choice([None, 1, 2])
            ))
        cur.executemany("""INSERT INTO produits (nom, id_categorie, prix, stock, id_promo)
                        VALUES (?, ?, ?, ?, ?)""", produits)
        
        # Peuplement des clients (50 exemples)
        villes = ["Paris", "Lyon", "Marseille", "Toulouse"]
        clients = []
        for i in range(1, 51):
            clients.append((
                f"Client {i}",
                f"client{i}@example.com",
                random.choice(villes)
            ))
        cur.executemany("INSERT INTO clients (nom, email, ville) VALUES (?, ?, ?)", clients)
        
        # Génération des ventes (200-300 exemples)
        start_date = datetime(2024, 1, 1)
        for _ in range(random.randint(200, 300)):
            date_vente = start_date + timedelta(days=random.randint(0, 364))
            id_produit = random.randint(1, 20)
            id_client = random.randint(1, 50)
            quantite = random.randint(1, 5)
            
            # Récupération du prix
            cur.execute("SELECT prix FROM produits WHERE id_produit = ?", (id_produit,))
            prix = cur.fetchone()[0]
            montant = round(prix * quantite, 2)
            
            cur.execute("""INSERT INTO ventes (id_produit, id_client, date_vente, quantite, montant)
                        VALUES (?, ?, ?, ?, ?)""",
                        (id_produit, id_client, date_vente.strftime("%Y-%m-%d"), quantite, montant))
        
        conn.commit()
        print(f" Base peuplée avec {cur.lastrowid} enregistrements")
    
    except Exception as e:
        print(f" Erreur : {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    peupler_db()