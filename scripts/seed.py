# Exemple de script pour insérer des données de démonstration
from novastore.models import Produit, catalogue


def seed():
    catalogue.extend([
        Produit(1, "Exemple", 100, "/static/images/sample.jpg", "Demo", "Description demo")
    ])


if __name__ == '__main__':
    seed()
    print('Seeding done')
