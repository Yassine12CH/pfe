from flask import Flask, request, jsonify
from flask_cors import CORS
from ortools.sat.python import cp_model

app = Flask(__name__)
CORS(app)

@app.route('/optimize', methods=['POST'])
def optimize():
    data = request.get_json()

    panel_width = data.get('width')
    panel_height = data.get('height')
    sections = data.get('sections')

    if not panel_width or not panel_height or not sections:
        return jsonify({"error": "Paramètres manquants (width, height, sections)."}), 400

    try:
        # Multiplier par 100 pour convertir en entiers
        scale_factor = 100
        panel_width = int(float(panel_width) * scale_factor)
        panel_height = int(float(panel_height) * scale_factor)
        sections = [
            {"width": int(float(section["width"]) * scale_factor), "height": int(float(section["height"]) * scale_factor)}
            for section in sections
        ]

        model = cp_model.CpModel()

        x_vars = []
        y_vars = []
        placements = []

        for i, section in enumerate(sections):
            width = section['width']
            height = section['height']

            # Définir les variables x et y pour chaque section
            x = model.NewIntVar(0, panel_width - width, f"x_{i}")
            y = model.NewIntVar(0, panel_height - height, f"y_{i}")
            x_vars.append(x)
            y_vars.append(y)
            placements.append((x, y, width, height))

        # Contraintes pour éviter les chevauchements
        for i in range(len(placements)):
            for j in range(i + 1, len(placements)):
                xi, yi, wi, hi = placements[i]
                xj, yj, wj, hj = placements[j]

                no_overlap_x1 = model.NewBoolVar(f"no_overlap_x1_{i}_{j}")
                no_overlap_x2 = model.NewBoolVar(f"no_overlap_x2_{i}_{j}")
                no_overlap_y1 = model.NewBoolVar(f"no_overlap_y1_{i}_{j}")
                no_overlap_y2 = model.NewBoolVar(f"no_overlap_y2_{i}_{j}")

                model.Add(xi + wi <= xj).OnlyEnforceIf(no_overlap_x1)
                model.Add(xj + wj <= xi).OnlyEnforceIf(no_overlap_x2)
                model.Add(yi + hi <= yj).OnlyEnforceIf(no_overlap_y1)
                model.Add(yj + hj <= yi).OnlyEnforceIf(no_overlap_y2)

                model.AddBoolOr([no_overlap_x1, no_overlap_x2, no_overlap_y1, no_overlap_y2])

        # Résolution du modèle
        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            result = []
            for i, (x, y, w, h) in enumerate(placements):
                # Diviser par 100 pour revenir aux dimensions originales
                result.append({
                    "id": i,
                    "x": solver.Value(x) / scale_factor,
                    "y": solver.Value(y) / scale_factor,
                    "width": w / scale_factor,
                    "height": h / scale_factor
                })
            return jsonify({"cuts": result})
        else:
            return jsonify({"error": "Aucune solution trouvée."}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
