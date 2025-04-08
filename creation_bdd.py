import sqlite3
from pathlib import Path
import os

# Chemin du nouveau fichier
db_path = Path(__file__).parent.parent / 'data' / 'ventes_2024.db'
os.makedirs(db_path.parent, exist_ok=True)

# Schéma optimisé
schema_sql = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS categories (
    id_categorie INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS promotions (
    id_promo INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    remise REAL CHECK (remise BETWEEN 0 AND 100),
    date_debut TEXT NOT NULL,
    date_fin TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS produits (
    id_produit INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    id_categorie INTEGER REFERENCES categories(id_categorie),
    prix REAL NOT NULL CHECK (prix > 0),
    stock INTEGER DEFAULT 0,
    id_promo INTEGER REFERENCES promotions(id_promo)
);

CREATE TABLE IF NOT EXISTS clients (
    id_client INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    email TEXT UNIQUE,
    ville TEXT
);

CREATE TABLE IF NOT EXISTS ventes (
    id_vente INTEGER PRIMARY KEY AUTOINCREMENT,
    id_produit INTEGER REFERENCES produits(id_produit),
    id_client INTEGER REFERENCES clients(id_client),
    date_vente TEXT NOT NULL,
    quantite INTEGER NOT NULL CHECK (quantite > 0),
    montant REAL NOT NULL
);

CREATE INDEX idx_ventes_date ON ventes(date_vente);
"""

# Exécution
try:
    with sqlite3.connect(str(db_path)) as conn:
        conn.executescript(schema_sql)
    print(f" Base créée : {db_path}")
except Exception as e:
    print(f" Erreur : {e}")