from flask import Blueprint, jsonify, request, session

api_bp = Blueprint('api', __name__)

@api_bp.route('/panier/ajouter', methods=['POST'])
def ajouter():
    data = request.json or {}
    if 'panier' not in session: session['panier'] = []
    if 'id' in data:
        session['panier'].append(int(data['id']))
        session.modified = True
    return jsonify({"status": "success", "total": len(session.get('panier', []))})

@api_bp.route('/panier/modifier', methods=['POST'])
def modifier_qte():
    data = request.json or {}
    p_id = int(data.get('id')) if data.get('id') else None
    action = data.get('action')
    if 'panier' in session and p_id is not None:
        if action == 'plus':
            session['panier'].append(p_id)
        elif action == 'moins':
            if p_id in session['panier']:
                session['panier'].remove(p_id)
        session.modified = True
    return jsonify({"status": "success"})

@api_bp.route('/panier/supprimer', methods=['POST'])
def supprimer():
    data = request.json or {}
    p_id = int(data.get('id')) if data.get('id') else None
    if p_id is not None and 'panier' in session:
        session['panier'] = [pid for pid in session['panier'] if pid != p_id]
        session.modified = True
    return jsonify({"status": "success"})
