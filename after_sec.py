import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session
from flask_wtf.csrf import CSRFProtect

# Charger les variables du fichier .env
load_dotenv()

app = Flask(__name__)

# Configuration de la clé secrète via .env
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'cle_fallback_si_env_manquant')

# Activer la protection CSRF globale
csrf = CSRFProtect(app)

# replacing :
if __name__ == '__main__':
    app.run(debug=True)
    
#By :
    
if __name__ == '__main__':
    # Mode debug désactivé par défaut en production
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ['true', '1']
    app.run(debug=debug_mode)
    
        
# CODE VULNÉRABLE (IDOR)
@app.route('/maj_poids', methods=['POST'])
def maj_poids():
    user_id = request.form.get('user_id')  # <-- DANGER ! Un attaquant peut changer cette valeur dans Inspecter Element
    nouveau_poids = request.form.get('poids')
    
    # Met à jour le poids de n'importe quel ID spécifié !
    db.execute("UPDATE users SET poids = ? WHERE id = ?", (nouveau_poids, user_id))
    
    
# CODE SÉCURISÉ
@app.route('/maj_poids', methods=['POST'])
def maj_poids():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    user_id = session['user_id']  # <-- SÉCURISÉ : Provient de la session serveur chiffrée
    nouveau_poids = request.form.get('poids')
    
    db.execute("UPDATE users SET poids = ? WHERE id = ?", (nouveau_poids, user_id))
    
    
                