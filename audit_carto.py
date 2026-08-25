import ast
import re
import os

APP_FILE = "app.py"

def analyser_cartographie(fichier):
    if not os.path.exists(fichier):
        print(f"[-] Erreur : Le fichier {fichier} est introuvable dans le dossier actuel.")
        return

    with open(fichier, "r", encoding="utf-8") as f:
        contenu = f.read()

    print("==================================================")
    print(f"   CARTOGRAPHIE ET RECONNAISSANCE DE {fichier}")
    print("==================================================\n")

    # 1. Extraction des routes Flask
    print("[+] 1. INVENTAIRE DES ROUTES & ENDPOINTS :")
    try:
        tree = ast.parse(contenu)
        routes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    # Détection de @app.route(...)
                    if isinstance(decorator, ast.Call) and getattr(decorator.func, 'attr', None) == 'route':
                        route_path = decorator.args[0].value if decorator.args and hasattr(decorator.args[0], 'value') else "Inconnu"
                        
                        # Extraction des méthodes HTTP
                        methods = ["GET"] # Par défaut sur Flask
                        for kw in decorator.keywords:
                            if kw.arg == 'methods':
                                methods = [elt.value for elt in kw.value.elts] if hasattr(kw.value, 'elts') else ["Variables"]
                        
                        routes.append((route_path, methods, node.name))

        if routes:
            for path, methods, func in routes:
                print(f"  • Route: {path:<25} | Méthodes: {str(methods):<15} | Fonction: {func}()")
            print(f"  --> Total : {len(routes)} routes détectées.\n")
        else:
            print("  [!] Aucune route Flask trouvée via l'analyse AST.\n")

    except Exception as e:
        print(f"  [-] Erreur lors du parsing du code : {e}\n")

    # 2. Détection des variables et secrets sensibles
    print("[+] 2. ANCIENNES PRATIQUES & SECRETS CODÉS EN DUR :")
    secret_key_match = re.search(r"secret_key\s*=\s*['\"]([^'\"]+)['\"]", contenu, re.IGNORECASE)
    if secret_key_match:
        valeur = secret_key_match.group(1)
        if valeur.lower() in ["dev", "secret", "12345", "supersecret", "change_me"]:
            print(f"  [CRITIQUE] SECRET_KEY faible détectée en dur : '{valeur}'")
        else:
            print(f"  [AVERTISSEMENT] SECRET_KEY codée en dur dans le code : '{valeur}' (Utiliser un fichier .env)")
    else:
        print("  [OK] Pas de SECRET_KEY explicite en dur ou chargée dynamiquement.")

    # 3. Détection des interactions avec la base de données
    print("\n[+] 3. BASE DE DONNÉES & OPÉRATIONS CRITIQUES :")
    if "sqlite3" in contenu:
        print("  • Moteur : SQLite (Module natif `sqlite3`)")
        if "execute(" in contenu and "%" in contenu or "format(" in contenu:
            print("  [AVERTISSEMENT] Risque potentiel de SQL Injection (Requêtes formatées avec string/format)")
    elif "flask_sqlalchemy" in contenu or "SQLAlchemy" in contenu:
        print("  • Moteur : ORM SQLAlchemy / Flask-SQLAlchemy (Sécurité renforcée par défaut)")
    else:
        print("  • Moteur non identifié automatiquement.")

    # 4. Vérification des protections globales
    print("\n[+] 4. CHECKLIST DE SÉCURITÉ RAPIDE :")
    protections = {
        "CSRF Protection": "CSRFProtect" in contenu or "WTForms" in contenu,
        "Gestion des Sessions": "session[" in contenu,
        "Gestion Mots de Passe (Bcrypt/Werkzeug)": "generate_password_hash" in contenu or "bcrypt" in contenu,
        "Débogage Flask (debug=True)": "debug=True" in contenu or "debug = True" in contenu
    }

    for item, statut in protections.items():
        symbol = "[OK]" if statut else "[A VÉRIFIER]"
        if item == "Débogage Flask (debug=True)" and statut:
            symbol = "[CRITIQUE]" # Le mode debug activé en prod est dangereux
        print(f"  {symbol:<15} {item}")

    print("\n==================================================")
    print("   FIN DE L'ANALYSE DE CARTOGRAPHIE")
    print("==================================================")

if __name__ == "__main__":
    analyser_cartographie(APP_FILE)