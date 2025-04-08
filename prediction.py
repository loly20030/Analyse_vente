import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from pathlib import Path
import sqlite3

# Configuration
DB_PATH = "data/ventes_2024.db"
GRAPHIQUES_DIR = Path("rapport/graphiques")
GRAPHIQUES_DIR.mkdir(parents=True, exist_ok=True)
TAUX_CONVERSION = 655.957  # 1 EUR = 655.957 FCFA

try:
    # 1. Connexion et chargement
    conn = sqlite3.connect(DB_PATH)
    
    # Requête SQL sans commentaires
    query = """
        SELECT v.date_vente, v.montant, 
               (v.montant * ?) as montant_fcfa
        FROM ventes v
    """
    
    df = pd.read_sql_query(query, conn, params=(TAUX_CONVERSION,))
    
    # 2. Vérification des données
    print("\n=== DONNÉES CHARGÉES ===")
    print("Colonnes disponibles:", df.columns.tolist())
    print("\nAperçu des données:")
    print(df.head(3))
    
    if 'montant_fcfa' not in df.columns:
        raise KeyError("La colonne montant_fcfa est manquante après la requête SQL")

    # 3. Préparation des données
    df['date_vente'] = pd.to_datetime(df['date_vente'])
    df['jour_annee'] = df['date_vente'].dt.dayofyear
    
    # 4. Modèle de prédiction
    X = df[['jour_annee']]
    y = df['montant_fcfa']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)

    # 5. Visualisation
    plt.figure(figsize=(12, 6))
    plt.scatter(X, y, color='blue', alpha=0.3, label="Données réelles")
    plt.plot(X, model.predict(X), color='red', linewidth=2, label="Prédiction")
    
    plt.title("Prévision du chiffre d'affaires annuel", fontsize=14)
    plt.xlabel("Jour de l'année", fontsize=12)
    plt.ylabel("Montant (FCFA)", fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # 6. Sauvegarde
    plt.savefig(GRAPHIQUES_DIR / "prevision_ca.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("\n Prédiction terminée - Graphique sauvegardé dans 'rapport/graphiques/prevision_ca.png'")

except sqlite3.Error as e:
    print(f"\n Erreur SQLite: {e}")
    print("Vérifiez que:")
    print("- La base de données existe bien à l'emplacement 'data/ventes_2024.db'")
    print("- La table 'ventes' contient les colonnes 'date_vente' et 'montant'")
    
except Exception as e:
    print(f"\n Erreur inattendue: {e}")
    
finally:
    if 'conn' in locals():
        conn.close()