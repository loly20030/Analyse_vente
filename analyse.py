import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import os

# Configuration des chemins et constantes
BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / 'data' / 'ventes_2024.db'
RAPPORT_DIR = BASE_DIR / 'rapport'
GRAPHIQUES_DIR = RAPPORT_DIR / 'graphiques'
EXPORTS_DIR = RAPPORT_DIR / 'exports'
TAUX_CONVERSION = 655.957  # 1 EUR = 655.957 FCFA

# Dictionnaire pour les noms de mois en français
MOIS_FR = {
    'January': 'Janvier', 'February': 'Février', 'March': 'Mars',
    'April': 'Avril', 'May': 'Mai', 'June': 'Juin',
    'July': 'Juillet', 'August': 'Août', 'September': 'Septembre',
    'October': 'Octobre', 'November': 'Novembre', 'December': 'Décembre'
}

def setup_directories():
    """Crée les répertoires nécessaires s'ils n'existent pas"""
    try:
        GRAPHIQUES_DIR.mkdir(parents=True, exist_ok=True)
        EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f" Erreur création des dossiers : {e}")
        raise

def analyser_ventes():
    """Fonction principale d'analyse des ventes"""
    try:
        # Vérification des dossiers
        setup_directories()

        # Connexion et requête
        with sqlite3.connect(str(DB_PATH)) as conn:
            print("🔍 Connexion à la base de données établie...")
            
            # Requête SQL
            df = pd.read_sql("""
                SELECT v.date_vente, v.montant, p.nom as produit, 
                       c.nom as categorie, cl.nom as client,
                       pr.nom as promotion, pr.remise
                FROM ventes v
                JOIN produits p ON v.id_produit = p.id_produit
                JOIN categories c ON p.id_categorie = c.id_categorie
                JOIN clients cl ON v.id_client = cl.id_client
                LEFT JOIN promotions pr ON p.id_promo = pr.id_promo
            """, conn)

            # Vérification des données chargées
            print("\n=== VÉRIFICATION DES DONNÉES ===")
            print("Colonnes disponibles:", df.columns.tolist())
            print("\n3 premières lignes:")
            print(df.head(3))
            print("\nValeurs manquantes par colonne:")
            print(df.isnull().sum())

            # Nettoyage des données
            df['promotion'].fillna('Aucune', inplace=True)
            df['remise'].fillna(0, inplace=True)

            # Conversion des dates et de la devise
            df['date_vente'] = pd.to_datetime(df['date_vente'])
            df['mois'] = df['date_vente'].dt.month_name().map(MOIS_FR)
            
            # Conversion du montant en FCFA
            if 'montant' not in df.columns:
                raise KeyError("La colonne 'montant' est introuvable dans les données!")
            
            df['montant_fcfa'] = df['montant'] * TAUX_CONVERSION
            print("\nAprès conversion - Colonnes:", df.columns.tolist())

            # 1. Statistiques globales (en FCFA)
            print("\n=== STATISTIQUES GLOBALES ===")
            print(f"CA Total : {df['montant_fcfa'].sum():,.2f} FCFA")
            print(f"Moyenne/vente : {df['montant_fcfa'].mean():,.2f} FCFA")
            print(f"Nombre de ventes : {len(df):,}")

            # 2. Top produits (FCFA)
            top_produits = df.groupby('produit')['montant_fcfa'].sum().nlargest(5)
            print("\n=== TOP 5 PRODUITS (FCFA) ===")
            print(top_produits.to_string(float_format='{:,.2f} FCFA'.format))

            # 3. Visualisations
            plt.figure(figsize=(14, 10))
            
            # Graphique 1: CA mensuel (FCFA)
            plt.subplot(2, 1, 1)
            ca_mensuel = df.groupby('mois')['montant_fcfa'].sum()
            ca_mensuel.plot(
                kind='bar', color='skyblue', 
                title='Chiffre d\'affaires mensuel (2024 - FCFA)')
            plt.ylabel('Montant (FCFA)')
            plt.grid(axis='y', linestyle='--')

            # Graphique 2: Répartition par catégorie
            plt.subplot(2, 1, 2)
            df.groupby('categorie')['montant_fcfa'].sum().plot(
                kind='pie', autopct=lambda p: f'{p:.1f}%\n({p*sum(df["montant_fcfa"])/100:,.0f} FCFA)',
                title='Répartition du CA par catégorie (FCFA)',
                startangle=90, counterclock=False)
            plt.ylabel('')

            plt.tight_layout()
            
            # Sauvegarde des graphiques
            graphe_path = GRAPHIQUES_DIR / 'analyse_ventes_fcfa.png'
            plt.savefig(str(graphe_path), dpi=300, bbox_inches='tight')
            print(f"\n Graphique sauvegardé : {graphe_path}")

            # 4. Export des données (en FCFA uniquement)
            export_path = EXPORTS_DIR / 'donnees_ventes.xlsx'
            df.to_excel(str(export_path), index=False)
            print(f" Données exportées : {export_path}")

    except sqlite3.Error as e:
        print(f" Erreur SQLite : {e}")
    except KeyError as e:
        print(f" Colonne manquante : {e}")
        print("Colonnes disponibles:", df.columns.tolist() if 'df' in locals() else "DataFrame non chargé")
    except Exception as e:
        print(f" Erreur inattendue : {e}")
    finally:
        plt.close('all')

if __name__ == "__main__":
    print("=== DÉBUT DE L'ANALYSE ===")
    analyser_ventes()
    print("=== ANALYSE TERMINÉE ===")