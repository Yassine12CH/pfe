from flask import Flask, request, jsonify
from flask_cors import CORS
from ortools.sat.python import cp_model

app = Flask(__name__)
CORS(app)

@app.route('/optimize', methods=['POST'])
def optimize():
    data = request.get_json()

    # Vérification des paramètres nécessaires
    panel_width = data.get('width')
    panel_height = data.get('height')
    sections = data.get('sections')

    if not panel_width or not panel_height or not sections:
        return jsonify({"error": "Paramètres manquants (width, height, sections)."}), 400

    try:
        # Validation des dimensions du panneau
        panel_width = float(panel_width)
        panel_height = float(panel_height)
        if panel_width <= 0 or panel_height <= 0:
            return jsonify({"error": "Les dimensions du panneau doivent être positives."}), 400

        # Validation des sections
        for section in sections:
            if 'width' not in section or 'height' not in section:
                return jsonify({"error": "Chaque section doit inclure 'width' et 'height'."}), 400
            if section['width'] <= 0 or section['height'] <= 0:
                return jsonify({"error": f"Dimensions invalides pour la section {section}."}), 400
            if section['width'] > panel_width or section['height'] > panel_height:
                return jsonify({"error": "Une section est plus grande que le panneau."}), 400

        # Initialisation du modèle de programmation par contraintes
        model = cp_model.CpModel()

        x_vars = []
        y_vars = []
        placements = []

        # Déclaration des variables pour la position de chaque section
        for i, section in enumerate(sections):
            width = section['width']
            height = section['height']

            # Variables pour la position de chaque section sur le panneau
            x = model.NewIntVar(0, int(panel_width - width), f"x_{i}")
            y = model.NewIntVar(0, int(panel_height - height), f"y_{i}")
            x_vars.append(x)
            y_vars.append(y)
            placements.append((x, y, width, height))

        # Contraintes de non-chevauchement
        for i in range(len(placements)):
            for j in range(i + 1, len(placements)):
                xi, yi, wi, hi = placements[i]
                xj, yj, wj, hj = placements[j]

                # Variables booléennes pour chaque cas de non-chevauchement
                no_overlap_x1 = model.NewBoolVar(f"no_overlap_x1_{i}_{j}")
                no_overlap_x2 = model.NewBoolVar(f"no_overlap_x2_{i}_{j}")
                no_overlap_y1 = model.NewBoolVar(f"no_overlap_y1_{i}_{j}")
                no_overlap_y2 = model.NewBoolVar(f"no_overlap_y2_{i}_{j}")

                # Contraintes pour éviter les chevauchements horizontaux et verticaux
                model.Add(xi + wi <= xj).OnlyEnforceIf(no_overlap_x1)  # Section i à gauche de j
                model.Add(xj + wj <= xi).OnlyEnforceIf(no_overlap_x2)  # Section j à gauche de i
                model.Add(yi + hi <= yj).OnlyEnforceIf(no_overlap_y1)  # Section i en dessous de j
                model.Add(yj + hj <= yi).OnlyEnforceIf(no_overlap_y2)  # Section j en dessous de i

                # Une des conditions de non-chevauchement doit être vraie
                model.AddBoolOr([no_overlap_x1, no_overlap_x2, no_overlap_y1, no_overlap_y2])

        # Objectif : maximiser l'utilisation de l'espace du panneau sans gaspillage
        model.Minimize(
            sum(x_vars) + sum(y_vars)  # Cette fonction minimise la "distance" parcourue par les sections sur le panneau
        )

        # Résolution du modèle
        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        # Vérification du statut de la solution
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            results = []
            for i, section in enumerate(sections):
                # Retour des positions optimisées des sections
                results.append({
                    "id": i,
                    "x": solver.Value(x_vars[i]),
                    "y": solver.Value(y_vars[i]),
                    "width": section['width'],
                    "height": section['height']
                })
            return jsonify({"cuts": results})  # Retourner les résultats optimisés
        else:
            return jsonify({"error": "Aucune solution optimale trouvée."}), 400

    except ValueError as e:
        return jsonify({"error": f"Valeurs invalides : {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Erreur inattendue : {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)
