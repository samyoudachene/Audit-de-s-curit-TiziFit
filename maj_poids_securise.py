@app.route('/maj_poids', methods=['POST'])
def maj_poids():
    # 1. Vérification stricte de l'authentification
    if 'user_id' not in session:
        flash("Veuillez vous connecter pour modifier votre poids.", "warning")
        return redirect(url_for('login'))

    user = UserTracker.query.get(session['user_id'])
    
    if not user:
        session.clear()
        return redirect(url_for('login'))

    nouveau_poids = request.form.get('poids', type=float)

    # 2. Validation des bornes (Business Logic Validation)
    if nouveau_poids is not None:
        if nouveau_poids < 30.0 or nouveau_poids > 300.0:
            flash("Veuillez entrer un poids valide compris entre 30 et 300 kg.", "danger")
            return redirect(url_for('track'))

        user.poids = nouveau_poids
        
        if user.historique_poids:
            user.historique_poids += f",{nouveau_poids}"
        else:
            user.historique_poids = str(nouveau_poids)

        # Recalcul automatique des besoins
        user.objectif_calories = user.calculer_besoin_calories()

        db.session.commit()
        flash(f"Votre nouveau poids de {nouveau_poids} kg a été enregistré.", "success")
    else:
        flash("Valeur de poids invalide.", "danger")

    return redirect(url_for('track'))