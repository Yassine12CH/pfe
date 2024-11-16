from flask import Flask, request, jsonify
from flask_cors import CORS
from ortools.sat.python import cp_model  # OR-Tools pour l'optimisation

app = Flask(__name__)
CORS(app)

@app.route('/optimize', methods=['POST'])
def optimize():
    data = request.get_json()

    # Vérification des paramètres
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

        # Initialisation du solveur
        model = cp_model.CpModel()

        # Déclaration des variables pour chaque section (position x, y)
        x_vars = []
        y_vars = []
        placements = []

        for i, section in enumerate(sections):
            width = section['width']
            height = section['height']

            # Variables pour la position de la section (x, y)
            x = model.NewIntVar(0, int(panel_width - width), f"x_{i}")
            y = model.NewIntVar(0, int(panel_height - height), f"y_{i}")
            x_vars.append(x)
            y_vars.append(y)
            placements.append((x, y, width, height))

        # Contraintes de non-chevauchement : ajout des restrictions nécessaires
        for i in range(len(placements)):
            for j in range(i + 1, len(placements)):
                xi, yi, wi, hi = placements[i]
                xj, yj, wj, hj = placements[j]

                # Créer des variables booléennes pour chaque cas de non-chevauchement
                no_overlap_x1 = model.NewBoolVar(f"no_overlap_x1_{i}_{j}")
                no_overlap_x2 = model.NewBoolVar(f"no_overlap_x2_{i}_{j}")
                no_overlap_y1 = model.NewBoolVar(f"no_overlap_y1_{i}_{j}")
                no_overlap_y2 = model.NewBoolVar(f"no_overlap_y2_{i}_{j}")

                # Ajouter les contraintes de non-chevauchement
                model.Add(xi + wi <= xj).OnlyEnforceIf(no_overlap_x1)  # Section i à gauche de j
                model.Add(xj + wj <= xi).OnlyEnforceIf(no_overlap_x2)  # Section j à gauche de i
                model.Add(yi + hi <= yj).OnlyEnforceIf(no_overlap_y1)  # Section i en dessous de j
                model.Add(yj + hj <= yi).OnlyEnforceIf(no_overlap_y2)  # Section j en dessous de i

                # Une des conditions de non-chevauchement doit être vraie
                model.AddBoolOr([no_overlap_x1, no_overlap_x2, no_overlap_y1, no_overlap_y2])

        # Objectif : minimiser l'espace utilisé ou optimiser l'arrangement
        model.Minimize(
            sum(x_vars) + sum(y_vars)
        )

        # Résolution
        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        # Résultat
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            results = []
            for i, section in enumerate(sections):
                x = solver.Value(x_vars[i])
                y = solver.Value(y_vars[i])
                width = section['width']
                height = section['height']

                # Placement des dimensions au centre ou à l'extérieur
                if width > 100 and height > 100:  # Critère pour définir une "grande" section
                    dimension_position = "center"  # Placer les dimensions au centre
                else:
                    dimension_position = "outside"  # Placer les dimensions à l'extérieur

                results.append({
                    "id": i,
                    "x": x,
                    "y": y,
                    "width": width,
                    "height": height,
                    "label": f"{width} * {height}"
                })

            return jsonify({"cuts": results})
        else:
            return jsonify({"error": "Aucune solution optimale trouvée."}), 400

    except ValueError as e:
        return jsonify({"error": f"Valeurs invalides : {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Erreur inattendue : {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)
