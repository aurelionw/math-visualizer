from flask import Flask, request, jsonify, render_template
import sympy as sp
import re
import subprocess
import os
from Kurvendiskussionsrechner.modules.Kurvendiskussion import Kurvendiskussion
from Kurvendiskussionsrechner.modules.Rechenweg import Rechenweg


app = Flask(__name__)

@app.route('/')
def htmlprobe():
    # Beispieleingabe für die HTML-Ansicht
    example_function = "x^3 - 3*x + 2"
    return render_template('htmlprobe.html', example_function=example_function)

# Helper function to convert SymPy objects into JSON-compatible types
def convert_to_json_compatible(data):
    if isinstance(data, sp.Basic):
        # Convert SymPy expression to LaTeX format (for better rendering of e.g. square roots)
        return sp.latex(data)  # Returns a LaTeX-compatible string
    elif isinstance(data, dict):
        return {key: convert_to_json_compatible(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_to_json_compatible(item) for item in data]
    return data

@app.route('/api/simplify', methods=['POST'])
def simplify_expression():
    # Convert string expression to SymPy object and simplify it
    data = request.get_json()
    funktion_str = data.get('funktion')
    try:
        expr = sp.sympify(funktion_str)
        simplified_expr = sp.simplify(expr)
        latex_output = sp.latex(simplified_expr)
        return jsonify({"latex": latex_output})
    except (sp.SympifyError, ValueError):
        # In case of error, return original expression
        return jsonify({"latex": funktion_str})

@app.route('/api/kurvendiskussion', methods=['POST'])
def kurvendiskussion():
    data = request.get_json()
    funktion_str = data.get('funktion')
    selected_variable = data.get('variable', 'x')
    selected_options = data.get('selected')

    try:
        # Preprocess input: replace ^ with ** and fix implicit multiplication
        funktion_str = funktion_str.replace('^', '**')
        funktion_str = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', funktion_str)
        funktion_str = funktion_str.replace("−", "-")

        # Detect variables from input string dynamically
        detected_variables = re.findall(r'[a-zA-Z]+', funktion_str)
        if selected_variable not in detected_variables:
            selected_variable = detected_variables[0] if detected_variables else 'x'

        variable = sp.symbols(selected_variable)
        funktion = sp.sympify(funktion_str)

        # Initialize Kurvendiskussion instance
        kd = Kurvendiskussion(funktion, variable)
        latex_function = sp.latex(funktion)

        response = {'latex': latex_function, 'variable': selected_variable}

        ableitungen = set() # Track which derivatives to return

        # Zero-crossings
        if "Nullstellen" in selected_options:
            response['Nullstellen'] = convert_to_json_compatible(kd.nullstellen().get('Nullstellen', []))
            # Rechenweg für Nullstellen hinzufügen
            rechenweg_instance = Rechenweg(funktion, variable)
            rechenweg = rechenweg_instance.welche_rechnung_benutzen()
            response['Nullstellen_rechenweg'] = rechenweg.get("schritte", [])

        # y-axis intersection
        if "y-Achsenabschnitt" in selected_options:
            response['y-Achsenabschnitt'] = convert_to_json_compatible(
                kd.berechne_y_achsenabschnitt().get('y-Achsenabschnitt', "Nicht definiert")
            )

        # Extrema (minima/maxima)
        if "Extremstellen" in selected_options:
            response['Extremstellen'] = convert_to_json_compatible(
                kd.berechne_extremstellen().get('extremstellen', [])
            )
            ableitungen.add('erste')  # Mark first derivative as required
            # Add explanation for extrema
            rechenweg_instance = Rechenweg(funktion, variable)
            rechenweg = rechenweg_instance.welche_rechnung_benutzen()
            response['Extremstellen_rechenweg'] = rechenweg.get("schritte", [])

        # Inflection points
        if "Wendepunkte" in selected_options:
            response['Wendepunkte'] = convert_to_json_compatible(
                kd.berechne_wendepunkte().get('wendepunkte', [])
            )
            ableitungen.add('zweite')  # Mark second derivative as required
            # Add explanation for inflection points
            rechenweg_instance = Rechenweg(funktion, variable)
            rechenweg = rechenweg_instance.welche_rechnung_benutzen()
            response['Wendepunkte_rechenweg'] = rechenweg.get("schritte", [])

        # End behavior (limit analysis as x → ±∞)
        if "Verhalten im unendlichen" in selected_options:
            response['Verhalten im Unendlichen'] = convert_to_json_compatible(kd.verhalten_im_unendlichen())

        # Add selected derivatives to the response
        if ableitungen:
            response['Ableitungen'] = kd.ableitungen_anzeigen(ableitungen)

        return jsonify(response)

    except Exception as e:
        print(f"Fehler in der Verarbeitung von '{funktion_str}': {e}")
        return jsonify({'status': 'error', 'message': str(e)})


def format_polynomdivision_as_latex(dividend, divisor, steps):
    """
    Formats polynomial division steps as LaTeX for visual representation.
    """
    latex = []
    latex.append(f"\\text{{{sp.latex(dividend)}}} : \\left({sp.latex(divisor)}\\right)")
    latex.append("\\begin{array}{r|l}")

    for step in steps:
        if 'dividend' in step and 'quotient' in step:
            latex.append(f"{sp.latex(step['dividend'])} & {sp.latex(step['quotient'])} \\\\")
        if 'subtracted' in step:
            latex.append(f"-({sp.latex(step['subtracted'])}) \\\\")
        if 'remainder' in step:
            latex.append("\\hline")
            latex.append(f"{sp.latex(step['remainder'])} \\\\")

    latex.append("\\end{array}")
    return "\n".join(latex)


@app.route('/api/rechenweg', methods=['POST'])
def rechenweg():
    data = request.get_json()
    funktion_str = data.get('funktion')
    selected_variable = data.get('variable', 'x')   # Default to 'x' if no variable is specified

    try:
        # Preprocess input: replace power symbol and fix multiplication formatting
        funktion_str = funktion_str.replace("^", "**")  # Ensure correct exponent notation
        funktion_str = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', funktion_str)  # Insert multiplication symbol
        funktion_str = funktion_str.replace("−", "-").replace(" ", "")  # Handle unicode minus and remove spaces

        # Detect variables dynamically
        detected_variables = list(set(re.findall(r'[a-zA-Z]+', funktion_str)))
        if selected_variable not in detected_variables:
            selected_variable = detected_variables[0] if detected_variables else 'x'

        variable = sp.symbols(selected_variable)
        funktion = sp.sympify(funktion_str)

        # Initialize step-by-step explanation class
        rechenweg_instance = Rechenweg(funktion, variable)
        rechenweg_schritte = []  # Gesamte Schritte

        print(f"Bereinigte Funktion: {funktion}")

        # Perform polynomial division iteratively for degree ≥ 3
        while sp.Poly(funktion).degree() >= 3:
            polynomdivision_result = rechenweg_instance.welche_rechnung_benutzen()
            rechenweg_schritte.extend(polynomdivision_result.get("schritte", []))



       # Solve remaining polynomial (degree ≤ 2)
        if sp.Poly(funktion).degree() == 2:
            pq_result = rechenweg_instance.pq_formel()
            rechenweg_schritte.extend(pq_result.get("schritte", []))
        elif sp.Poly(funktion).degree() == 1:
           # Solve linear equation
            loesung = sp.solve(funktion, variable)
            rechenweg_schritte.append({
                "text": "Lineares Auflösen der Gleichung:",
                "latex": f"{sp.latex(funktion)} = 0 \\Rightarrow {sp.latex(loesung)}"
            })


        # Format all steps into LaTeX output
        latex_steps = []
        for step in rechenweg_schritte:
            latex_steps.append(f"{step.get('text', '')}: {step.get('latex', '')}")



        return jsonify({
            "Rechenweg": "\\\\ \n".join(latex_steps)

        })

    except Exception as e:
        print(f"Fehler in der Verarbeitung von '{funktion_str}': {e}")
        return jsonify({'status': 'error', 'message': str(e)})

""""
@app.route('/api/polynomdivision', methods=['POST'])
def polynomdivision():
    data = request.get_json()
    dividend = data.get('dividend')
    divisor = data.get('divisor')

    if not dividend or not divisor:
        return jsonify({"error": "Dividend und Divisor müssen angegeben werden."}), 400

    try:
        # Generiere und kompiliere den LaTeX-Code
        output_dir = "uploads"
        os.makedirs(output_dir, exist_ok=True)

        rechenweg = Rechenweg(None, None)  # Dummy-Instanz
        latex_code = rechenweg.generate_polynom_latex(dividend, divisor)
        pdf_path = rechenweg.compile_latex(latex_code, output_dir)

        return jsonify({"pdf_url": f"/{pdf_path}"})
    except Exception as e:
        print(f"Fehler bei der Polynomdivision: {e}")
        return jsonify({"error": str(e)}), 500

"""""



if __name__ == '__main__':
    app.run(debug=True)
