from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify
from collections import Counter
import uuid
from datetime import datetime, timedelta

from ..models import catalogue, produits_db
from ..poo_classes import Panier, Commande, Client, StatutCommande, Admin, PaiementCarte

main_bp = Blueprint('main', __name__)

# Simulation d'une base de données en mémoire pour les commandes
commandes_db = []

# Simulation d'une base de données pour les alertes stock
alertes_db = []

@main_bp.before_request
def make_session_permanent():
    session.permanent = True

# Helper pour reconstruire l'objet Panier depuis la session
def get_panier_session():
    ids_panier = session.get('panier', [])
    panier = Panier()
    comptage = Counter(ids_panier)
    for p_id, qte in comptage.items():
        p = produits_db.get(int(p_id))
        if p:
            panier.ajouter_article(p, qte)
    return panier

@main_bp.route('/')
def landing():
    # Récupération dynamique des catégories uniques depuis le catalogue
    counts = Counter(p.categorie for p in catalogue if p.categorie)
    categories = sorted(counts.keys())
    sections = [{'titre': c, 'btn': 'Voir la collection →', 'cat': c, 'count': counts[c]} for c in categories]
    
    return render_template('landing.html', sections=sections)

@main_bp.route('/boutique')
def boutique():
    cat = request.args.get('cat')
    promo = request.args.get('promo')
    
    produits_filtres = catalogue

    if cat:
        produits_filtres = [p for p in produits_filtres if str(p.categorie).strip() == cat.strip()]
    
    if promo:
        produits_filtres = [p for p in produits_filtres if p.promo > 0]

    return render_template('boutique.html', produits=produits_filtres)

@main_bp.route('/about')
def about():
    return render_template('about.html')

@main_bp.route('/livraison')
def livraison():
    return render_template('livraison.html')

@main_bp.route('/panier')
def voir_panier():
    panier = get_panier_session()
    articles_panier = []
    
    # Adaptation pour le template qui attend une liste de dicts ou objets compatibles
    for item in panier.articles:
        # On crée une structure compatible avec le template existant
        articles_panier.append({'produit': item.produit, 'quantite': item.quantite, 'sous_total': item.total_ligne()})
        
    return render_template('panier.html', articles=articles_panier, total=panier.calculer_total())

@main_bp.route('/panier/vider')
def vider_panier():
    session['panier'] = []
    session.modified = True
    flash("Votre panier a été vidé.", "success")
    return redirect(url_for('main.voir_panier'))

@main_bp.route('/checkout')
def checkout():
    panier = get_panier_session()
    if not panier.articles:
        return redirect(url_for('main.boutique'))
    return render_template('checkout.html', total=panier.calculer_total())

@main_bp.route('/success')
def success():
    panier = get_panier_session()
    if not panier.articles:
        return redirect(url_for('main.boutique'))

    # 1. Vérification des stocks via la méthode POO
    for item in panier.articles:
        if not item.produit.est_disponible(item.quantite):
            flash(f"Stock insuffisant pour {item.produit.nom}. Disponible : {item.produit.stock}", "error")
            return redirect(url_for('main.voir_panier'))

    # Création du Client (basé sur la session)
    user_str = session.get('user', 'Client Invité')
    # On instancie un objet Client (ID fictif pour l'exemple web)
    client = Client(id=1, nom=user_str, email="client@novastore.ma", mot_de_passe="", adresse="Adresse Web")

    # Création de la Commande
    order_number = f"NS-{str(uuid.uuid4())[:8].upper()}"
    commande = Commande(order_number, panier, client)
    
    # Simulation du paiement via POO (Utilisation de PaiementCarte)
    # Dans un vrai cas, on récupérerait les infos du formulaire
    paiement = PaiementCarte(commande.total, commande, "1234-5678-9012-3456", "123")
    paiement.payer() # Affiche le log en console et change le statut si implémenté

    # Validation POO (décrémente les stocks et change le statut)
    commande.confirmer_commande()
    
    # Ajout d'un attribut progression pour l'affichage web (non présent dans la classe de base)
    commande.progression = 25 

    # Sauvegarde dans la "base de données"
    # Utilisation de la méthode POO du client
    client.ajouter_commande_historique(commande)
    
    commandes_db.append(commande)

    # Sauvegarde de l'ID commande pour la page de succès/facture
    session['derniere_commande_id'] = order_number

    session['panier'] = []
    session.modified = True

    return render_template('success.html', order_number=order_number, total=commande.total)

@main_bp.route('/facture')
def facture():
    cmd_id = session.get('derniere_commande_id')
    commande = next((c for c in commandes_db if c.id_commande == cmd_id), None)
    
    if not commande:
        return redirect(url_for('main.boutique'))
        
    # On génère aussi la version texte POO pour montrer qu'on l'utilise
    facture_texte = commande.generer_facture(mode_paiement="Carte Bancaire")
    return render_template('facture.html', commande=commande, facture_texte=facture_texte)

@main_bp.route('/profil')
def profil():
    if 'user' not in session:
        return redirect(url_for('main.login'))
        
    # Simulation des données client (car session['user'] ne contient que le nom pour l'instant)
    user_nom = session['user']
    client = Client(id=1, nom=user_nom, email=f"{user_nom.lower().replace(' ', '.')}@gmail.com", mot_de_passe="***", adresse="123 Bd Zerktouni, Casablanca")
    
    return render_template('profil.html', client=client)

@main_bp.route('/commandes')
def commandes():
    if 'user' not in session:
        return redirect(url_for('main.login'))

    # Récupère les commandes de l'utilisateur connecté
    user = session.get('user')
    
    # Simulation : Passage automatique à "Livrée" après 5 secondes pour le test
    for cmd in commandes_db:
        if cmd.statut == StatutCommande.EN_COURS and (datetime.now() - cmd.date_commande).total_seconds() > 5:
            cmd.statut = StatutCommande.LIVREE
            cmd.progression = 100
            flash(f"Votre commande {cmd.id_commande} a été livrée !", "success")
            
    mes_commandes = [cmd for cmd in commandes_db if cmd.client.nom == user]
    
    return render_template('commandes.html', commandes=list(reversed(mes_commandes)))

@main_bp.route('/commande/annuler/<string:oid>')
def annuler_commande(oid):
    if 'user' not in session:
        return redirect(url_for('main.login'))
    
    user = session['user']
    for cmd in commandes_db:
        # On vérifie que la commande appartient bien à l'utilisateur
        if cmd.id_commande == oid and cmd.client.nom == user:
            if cmd.statut == StatutCommande.EN_COURS: # Correspond à "En cours" après confirmation
                cmd.statut = StatutCommande.ANNULEE
                cmd.progression = 0
                flash("Commande annulée avec succès.", "success")
            break
    return redirect(url_for('main.commandes'))

@main_bp.route('/commande/recommander/<string:oid>')
def recommander(oid):
    if 'user' not in session:
        return redirect(url_for('main.login'))
    
    user = session['user']
    target_cmd = None
    for cmd in commandes_db:
        if cmd.id_commande == oid and cmd.client.nom == user:
            target_cmd = cmd
            break
            
    if target_cmd:
        panier = session.get('panier', [])
        # On rajoute chaque produit de la commande dans le panier actuel
        for item in target_cmd.items:
            # item est un objet Panierltem
            for _ in range(item.quantite):
                panier.append(item.produit.id)
        session['panier'] = panier
        session.modified = True
        flash("Les produits ont été ajoutés à votre panier.", "success")
        return redirect(url_for('main.voir_panier'))
    
    flash("Commande introuvable.", "error")
    return redirect(url_for('main.commandes'))

@main_bp.route('/api/panier/ajouter', methods=['POST'])
def ajouter_panier_api():
    data = request.get_json()
    p_id = int(data.get('id'))
    
    produit = produits_db.get(p_id)
    if not produit:
        return jsonify({'error': 'Produit introuvable'}), 404

    panier = session.get('panier', [])
    # On compte combien de fois ce produit est déjà dans le panier
    qte_actuelle = panier.count(p_id)
    
    if not produit.est_disponible(qte_actuelle + 1):
        return jsonify({'error': f"Stock insuffisant. Max: {produit.stock}"}), 400
        
    panier.append(p_id)
    session['panier'] = panier
    session.modified = True
    return jsonify({'total': len(panier), 'message': 'Produit ajouté'})

@main_bp.route('/api/panier/modifier', methods=['POST'])
def modifier_panier_api():
    data = request.get_json()
    p_id = int(data.get('id'))
    action = data.get('action')
    
    panier_ids = session.get('panier', [])
    
    if action == 'plus':
        produit = produits_db.get(p_id)
        if produit:
            current_qty = panier_ids.count(p_id)
            if produit.est_disponible(current_qty + 1):
                panier_ids.append(p_id)
            else:
                return jsonify({'status': 'error', 'message': f'Stock insuffisant (Max: {produit.stock})'})
    elif action == 'moins':
        if p_id in panier_ids:
            panier_ids.remove(p_id)
            
    session['panier'] = panier_ids
    session.modified = True
    
    # Recalcul des totaux
    panier_obj = get_panier_session()
    item_data = next((item for item in panier_obj.articles if item.produit.id == p_id), None)
    
    return jsonify({
        'status': 'success',
        'total': panier_obj.calculer_total(),
        'item_qty': item_data.quantite if item_data else 0,
        'item_total': item_data.total_ligne() if item_data else 0,
        'cart_count': len(panier_ids)
    })

@main_bp.route('/api/panier/supprimer', methods=['POST'])
def supprimer_panier_api():
    data = request.get_json()
    p_id = int(data.get('id'))
    
    panier_ids = session.get('panier', [])
    panier_ids = [pid for pid in panier_ids if pid != p_id]
    
    session['panier'] = panier_ids
    session.modified = True
    
    panier_obj = get_panier_session()
    
    return jsonify({
        'status': 'success',
        'total': panier_obj.calculer_total(),
        'cart_count': len(panier_ids)
    })

@main_bp.route('/api/alert/subscribe', methods=['POST'])
def subscribe_alert():
    data = request.get_json()
    p_id = int(data.get('id'))
    email = data.get('email')
    
    if not email or '@' not in email:
        return jsonify({'error': 'Email invalide'}), 400
        
    # Vérifie si l'alerte existe déjà
    if not any(a['product_id'] == p_id and a['email'] == email for a in alertes_db):
        alertes_db.append({'product_id': p_id, 'email': email})
        
    return jsonify({'message': 'Alerte enregistrée ! Vous serez notifié.'})


# --- AUTHENTIFICATION (Login, Register, Password) ---

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Simulation de connexion simple
        email = request.form.get('email')
        user_name = email.split('@')[0] if email else "Client"
        session['user'] = user_name
        flash(f"Ravi de vous revoir, {user_name} !", "success")
        return redirect(url_for('main.boutique'))
    return render_template('login.html')

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        flash("Compte créé avec succès ! Vous pouvez vous connecter.", "success")
        return redirect(url_for('main.login'))
    return render_template('register.html')

@main_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        flash("Un lien de réinitialisation a été envoyé à votre adresse email.", "success")
        return redirect(url_for('main.login'))
    return render_template('forgot_password.html')

# --- SECTION ADMIN ---

@main_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # On instancie l'admin (Login: admin@novastore.ma / Pass: admin123)
        admin = Admin(id=999, nom="Super Admin", email="admin@novastore.ma", mot_de_passe="admin123")
        
        # Utilisation de la méthode POO se_connecter
        if admin.se_connecter(email, password):
            session['admin_user'] = admin.nom
            session['user'] = admin.nom # Pour afficher le menu profil
            flash(f"Bienvenue {admin.nom}", "success")
            return redirect(url_for('main.admin_dashboard'))
        else:
            flash("Identifiants incorrects", "error")
            
    return render_template('admin_login.html')

@main_bp.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_user' not in session:
        return redirect(url_for('main.admin_login'))
    
    # Filtrage par date
    period = request.args.get('period', 'all')
    now = datetime.now()
    start_date = None
    
    if period == 'today':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == 'week':
        start_date = now - timedelta(days=7)
    elif period == 'month':
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Stats pour le graphique
    ventes = {}
    ca_par_jour = {}
    kpi_orders_count = 0
    
    for cmd in commandes_db:
        if cmd.statut != StatutCommande.ANNULEE:
            if start_date and cmd.date_commande < start_date:
                continue
            
            kpi_orders_count += 1
                
            # Ventes par produit
            for item in cmd.items:
                p_nom = item.produit.nom
                ventes[p_nom] = ventes.get(p_nom, 0) + item.quantite
            
            # CA par jour
            date_key = cmd.date_commande.strftime('%d/%m')
            ca_par_jour[date_key] = ca_par_jour.get(date_key, 0) + cmd.total
            
    kpi_revenue = sum(ca_par_jour.values())
    kpi_low_stock = len([p for p in catalogue if p.stock < 5])
                
    return render_template('admin_dashboard.html', 
                           produits=catalogue, 
                           alertes=alertes_db, 
                           chart_labels=list(ventes.keys()), 
                           chart_data=list(ventes.values()),
                           revenue_labels=list(ca_par_jour.keys()),
                           revenue_data=list(ca_par_jour.values()),
                           current_period=period,
                           kpi_revenue=kpi_revenue,
                           kpi_orders=kpi_orders_count,
                           kpi_low_stock=kpi_low_stock)

@main_bp.route('/admin/restock', methods=['POST'])
def admin_restock():
    if 'admin_user' not in session:
        return redirect(url_for('main.admin_login'))
        
    p_id = int(request.form.get('product_id'))
    qty = int(request.form.get('quantity'))
    produit = produits_db.get(p_id)
    
    if produit:
        admin = Admin(id=999, nom=session['admin_user'], email="admin@novastore.ma", mot_de_passe="***")
        try:
            # Utilisation de la méthode POO reaprovisionner
            msg = admin.reaprovisionner(produit, qty)
            
            # Gestion des alertes
            alerts_to_send = [a for a in alertes_db if a['product_id'] == p_id]
            for alert in alerts_to_send:
                print(f"📧 ALERTE STOCK: Email envoyé à {alert['email']} pour {produit.nom}")
                alertes_db.remove(alert)
                
            flash(f"{msg} ({len(alerts_to_send)} alertes envoyées)", "success")
        except ValueError as e:
            flash(str(e), "error")
            
    return redirect(url_for('main.admin_dashboard'))

@main_bp.route('/admin/logout')
def admin_logout():
    session.pop('admin_user', None)
    return redirect(url_for('main.admin_login'))
