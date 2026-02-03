# 🛍️ Novastore - Plateforme E-Commerce (Projet POO Python)

**Novastore** est une application web e-commerce développée dans le cadre du module de **Programmation Orientée Objet (POO)** à l'**ENSA Khouribga**. L'objectif est de démontrer l'application des concepts POO au sein d'une architecture Web moderne (Flask).

---

## 🧬 Concepts POO Matérialisés

Contrairement à un script simple, ce projet repose sur une structure d'objets rigoureuse située dans `novastore/models.py` et `novastore/poo_classes.py` :

- **Encapsulation** : Gestion sécurisée des données utilisateurs et des attributs produits.
- **Abstraction** : Modélisation des entités réelles (Utilisateur, Produit, Commande) en classes Python.
- **Persistance des Objets** : Utilisation de SQLAlchemy pour mapper nos objets POO vers une base de données relationnelle.
- **Logique Métier** : Méthodes de classe pour le calcul des totaux, la gestion des stocks et la validation des paniers.

---

## 🚀 Fonctionnalités du Système

- **Gestion des Utilisateurs** : Inscription, connexion et sessions sécurisées.
- **Catalogue & Recherche** : Filtrage par catégories et moteur de recherche intégré.
- **Système de Panier API** : Interaction dynamique pour l'ajout et la modification d'articles.
- **Génération de Factures** : Transformation des objets "Commande" en documents exploitables.
- **Dashboard Admin** : Interface de gestion CRUD (Create, Read, Update, Delete) pour les administrateurs.

---

## 🏗️ Architecture du Projet

```text
novastore/
├── app.py                 # Point d'entrée Flask
├── run.py                 # Script de lancement
├── novastore/
│   ├── models.py          # Définition des classes POO (SQLAlchemy)
│   ├── poo_classes.py     # Logique métier spécifique
│   └── routes/            # Blueprints (Contrôleurs)
├── templates/             # Interface utilisateur (Jinja2)
├── static/                # Design (CSS, JS, Images)
└── scripts/               # Scripts de peuplement (Seed)
```
---
## 👥 Équipe de Projet (ENSA Khouribga)
*Filière : Informatique et Ingénierie des Données (IID)*

* **Azeddine Maktou**
* **Othmane Laaouina**
* **Godwin Elie Nougbolo**
* **Mariam M’barki**
* **Kawtar Mahboub El Idrissi**
```
© 2025 - **École Nationale des Sciences Appliquées de Khouribga**
