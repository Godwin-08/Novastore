from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from enum import Enum

#Classe categorie
class Categorie:#Représente une famille de produits (ex: Poables, Vêtements ...)

    def __init__(self,id,nom):
        
        self.id=id
        self.nom=nom 
        self.produits=[] # ou on stocke les objets produits d'une categorie

    def ajouter_produit(self,produit):  #ajoute le produit a la liste de sa categorie
        #on verifie si le produit n'existe pas deja dans la categorie pour eviter les doublants
        if produit not in self.produits:
            self.produits.append(produit)
            produit.categorie=self # On lie aussi le produit à cette catégorie (relation bidirectionnelle)
        else :
            print(f"Information: {produit.nom} existe déjà dans {self.nom}.")

    def __str__(self): #return le nom de la categorie
        return self.nom



#Classe Produit
class Produit():
  def __init__(self,id,nom,prix,image,categorie,description="",promo=0,stock=50):

    self.id=id
    self.nom=nom
    self.prix=prix
    self.image=image
    self.categorie = categorie
    self.description=description
    self.promo=promo
    self.stock=stock
# sera definie par l'objet categorie.ajouterProduit

  def est_disponible(self,quantite_demandee=1):
    #Retourne True si le stock est suffisant pour la quantité demandée.
      return self.stock>=quantite_demandee
  
  def mettre_a_jour_stock(self,quantite_vendue):
     #Diminue le stock apres la vente et donnne une erreur si le stock est insuffisant
     if quantite_vendue<0:
        raise ValueError("La quantité vendue ne peut pas être négative")
     #On vérifie le stock AVANT de soustraire
     if self.est_disponible(quantite_vendue):
            self.stock -= quantite_vendue
     else:
        raise ValueError(f"Le stock est insuffisant pour {self.nom}.Disponible:{self.stock}")
   
  def __str__(self):
   #Afffiche une descriptio textuelle pour le produit
   return f"Le produit:{self.nom} coûte {self.prix} en qantité de :{self.stock}"

  def to_dict(self):
      return {
          "id": self.id,
          "nom": self.nom,
          "prix": self.prix,
          "image": self.image,
          "categorie": str(self.categorie),
          "description": self.description,
          "promo": self.promo,
          "stock": self.stock
      }
     



#Classe mere Utilisateur
# on cree une classe abstraite car on ne peut pas creer un utilisateur simple il peut etre soit client ou admin
class Utilisateur(ABC):
  def __init__(self,id,nom,email,mot_de_passe):
    self.id=id
    self.nom=nom
    self.email=email
    self.__mot_de_passe=mot_de_passe #attribut prive pour la securite

  def se_connecter(self,sonEmail,sonMotDePasse):
    #verifie si l'email et le mot de passe sonr correspondants si oui return True.
    return self.email==sonEmail and self.__mot_de_passe==sonMotDePasse
  
  @abstractmethod
  def get_role(self):
    # une methode abstraite ,oblige ses enfant client et admin a definir leur role
    pass
  
  
  #classe fille 1: Client
class Client(Utilisateur):

    def __init__(self,id,nom,email,mot_de_passe,adresse):
        # appel du constructeur de la classe mere Utilisateur
        super().__init__(id,nom,email,mot_de_passe)
        self.adresse=adresse
        self.historique_commande=[]  #liste ou on stocke les objets commande
        self.cartes_enregistrees=[]  # liste des numeros de cartes mais (str)

    def get_role(self):
        #indique que cet utilisateur est un client
        return "Client"
    
    def ajouter_commande_historique(self,commande):
        #ajoute une commande validee a l'historique
        self.historique_commande.append(commande)

    def ajouter_carte(self,numero_carte):
      if len(str(numero_carte))!=16:
         raise ValueError("Numéro de la carte est invalide ")
      self.cartes_enregistrees.append(str(numero_carte))


   #Classe fille 2:admin
class Admin(Utilisateur):

    def __init__(self,id,nom,email,mot_de_passe):
        super().__init__(id,nom,email,mot_de_passe)
    
    def get_role(self):
        return "Admin"
    
    def reaprovisionner(self,produit,quantite):
        if quantite <=0 :
            raise ValueError("La quantité à réapprovisionner doit être positive.")
        
        produit.stock+=quantite
        return f"Le stock de {produit.nom} est maintenant {produit.stock}"


########################################## part 2 ###########################################


class Panierltem:
    def __init__(self, produit, quantite):
            self.produit = produit  # Instance de la classe Produit
            self.quantite = quantite  # Quantité du produit dans le panier

    def total_ligne(self):
            # Calcule le total pour cette ligne (produit * quantité)
            return self.produit.prix * self.quantite
    
    def __str__(self):
            return f"{self.produit.nom} x {self.quantite} = {self.total_ligne():.2f} DH"
    
class Panier:
    def __init__(self):
        self.articles = []  # Liste des objets Panierltem

    def ajouter_article(self, produit, quantite):
        # Vérifie si le produit est déjà dans le panier
        for item in self.articles:
            if item.produit.id == produit.id:
                item.quantite += quantite  # Met à jour la quantité
                return
        # Si le produit n'est pas dans le panier, l'ajoute
        self.articles.append(Panierltem(produit, quantite))

    def retirer_article(self, produit_id):
        # Retire un article du panier en fonction de son ID
        self.articles = [item for item in self.articles if item.produit.id != produit_id]
            
    def calculer_total(self):
        # Calcule le total du panier
        return sum(item.total_ligne() for item in self.articles)
    
    def vider_panier(self):
        # Vide le panier
        self.articles = []

    # Affichage du panier
    def __str__(self):
        if not self.articles:
            return "Le panier est vide."
        # Affiche les détails du panier
        details = "\n".join(str(item) for item in self.articles) 
        total = self.calculer_total()
        return f"Détails du panier:\n{details}\nTotal: {total:.2f} DH"

# etats de commande
class StatutCommande(Enum):
    EN_COURS = "En cours"
    EN_ATTENTE = "En attente"
    EXPEDIEE = "Expédiée"
    LIVREE = "Livrée"
    ANNULEE = "Annulée"

#Classe Commande
class Commande:
    def __init__(self, id_commande, panier, client):
        self.id_commande = id_commande
        self.statut = StatutCommande.EN_ATTENTE  # Statut initial de la commande
        self.total = panier.calculer_total()  # Total de la commande
        self.date_commande = datetime.now()  # Date et heure de la commande
        self.client = client  # Instance de la classe Client
        self.items = panier.articles.copy()  # Copie des articles du panier au moment de la commande

    def confirmer_commande(self):
      for item in self.items:
        item.produit.mettre_a_jour_stock(item.quantite)
      self.statut = StatutCommande.EN_COURS
      return True

    def get_facture_id(self):
        """Retourne l'identifiant formaté de la facture."""
        if isinstance(self.id_commande, int):
            return f"FACT-{self.id_commande:06d}"
        else:
            return f"FACT-{self.id_commande}"

    def generer_facture(self, mode_paiement="Non spécifié", adresse_livraison=None, date_livraison=None):
        """
        Génère une facture détaillée pour la commande.
    
        Args:
            mode_paiement (str): Mode de paiement utilisé (Carte, PayPal, etc.).
            adresse_livraison (str): Adresse de livraison si différente de celle du client.
            date_livraison (datetime.date, optional): Date estimée ou réelle de livraison.
        """
        adresse_livraison = adresse_livraison or self.client.adresse
        date_livraison_str = date_livraison.strftime('%Y-%m-%d') if isinstance(date_livraison, datetime) else (
            date_livraison.isoformat() if hasattr(date_livraison, 'isoformat') else (str(date_livraison) if date_livraison else "À déterminer")
        )

    # Détails des articles
        lignes = "\n".join(
            f"- {item.produit.nom} | Quantité: {item.quantite} | Prix unitaire: {item.produit.prix:.2f} DH | Total: {item.total_ligne():.2f} DH"
            for item in self.items
    )

        facture_id = self.get_facture_id()

        facture = (
            f"=================== FACTURE ===================\n"
            f"Entreprise: NovaStore\n"
            f"Adresse: 123 Rue du bonheur, Khouribga, Maroc\n"
            f"Numéro de facture: {facture_id}\n"
            f"Date de la facture: {self.date_commande.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Numéro de commande: {self.id_commande}\n"
            f"Mode de paiement: {mode_paiement}\n"
            f"Statut: {self.statut.value}\n"
            f"-----------------------------------------------\n"
            f"Client:\n"
            f"Nom: {self.client.nom}\n"
            f"Email: {self.client.email}\n"
            f"Téléphone: {getattr(self.client, 'tel', 'Non renseigné')}\n"
            f"Adresse de livraison: {adresse_livraison}\n"
            f"-----------------------------------------------\n"
            f"Détails des articles:\n{lignes}\n"
            f"-----------------------------------------------\n"
            f"Total à payer: {self.total:.2f} DH\n"
            f"Date estimée/réelle de livraison: {date_livraison_str}\n"
            f"\n"
            f"Merci pour votre commande chez NovaStore !\n"
            f"Nous espérons que nos produits vous satisferont pleinement.\n"
            f"================================================"
    )
        return facture

########################################## part 3 ###########################################

# Paiement abstrait
class Paiement(ABC):
    def __init__(self, montant, commande):
        self.montant = montant
        self.commande = commande

    @abstractmethod
    def payer(self):
        pass

class PaiementCarte(Paiement):
    def __init__(self, montant, commande, numero_carte, crypto):
        super().__init__(montant, commande)
        self.numero_carte = numero_carte
        self.__crypto = crypto  # Attribut privé (__crypto)

    def payer(self):
        print(f"Traitement du paiement par Carte ({self.numero_carte})...")
        print("Banque : Autorisation accordée.")
        self.commande.statut = StatutCommande.EN_COURS
        print(f"Paiement de {self.montant}€ validé. Statut commande mis à jour.")

class PaiementPayPal(Paiement):
    def __init__(self, montant, commande, email_paypal):
        super().__init__(montant, commande)
        self.email_paypal = email_paypal

    def payer(self):
        print(f"Redirection vers PayPal ({self.email_paypal})...")
        print("PayPal : Transaction validée.")
        self.commande.statut = StatutCommande.EN_COURS
        print(f"Paiement de {self.montant}€ reçu via PayPal.")