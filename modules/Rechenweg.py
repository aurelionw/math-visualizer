import sympy as sp
import random
import subprocess
import os

"""Class to provide step-by-step explanations for solving equations."""
class Rechenweg:

    def __init__(self, funktion, variable):
        self.funktion = funktion
        self.variable = variable
        self.ordnung = self.ordnung_der_funktion()

    def ordnung_der_funktion(self):
        """Determines the degree of the polynomial."""
        try:
            ordnung = sp.Poly(self.funktion).degree()
        except sp.PolynomialError:
            ordnung = None  # If the expression is not a polynomia
        return ordnung

    def pq_formel(self):
        """Applies the p-q formula and returns all calculation steps in LaTeX format."""
        funktion_als_liste = sp.Poly(self.funktion).all_coeffs()
        schritte = []  

        # Normalize if leading coefficient is not 1
        if funktion_als_liste[0] != 1:
            schritte.append({
                "text": f"Normiere die Funktion, da der Vorfaktor {funktion_als_liste[0]} ungleich 1 ist.",
                "latex": f"f(x) = {sp.latex(self.funktion)} \\rightarrow \\frac{{f(x)}}{{{funktion_als_liste[0]}}}"
            })
            funktion_als_liste = [k / funktion_als_liste[0] for k in funktion_als_liste]

        schritte.append({
            "text": "Normierte Koeffizienten:",
            "latex": f"p = {funktion_als_liste[1]}, \\ q = {funktion_als_liste[2]}"
        })

        p = funktion_als_liste[1]
        q = funktion_als_liste[2]
        diskriminante = (p / 2) ** 2 - q

        schritte.append({
            "text": "Berechnung der Diskriminante:",
            "latex": f"\\left( \\frac{{p}}{{2}} \\right)^2 - q = \\left( \\frac{{{p}}}{{2}} \\right)^2 - {q} = {sp.latex(diskriminante)}"
        })

        # Handle complex roots
        if diskriminante < 0:
            schritte.append({
                "text": "Die Diskriminante ist negativ. Es existieren keine reellen Lösungen.",
                "latex": f"\\Delta = {sp.latex(diskriminante)} \\ (< 0)"
            })
            return {"schritte": schritte, "loesungen": "Komplexe Lösung nicht berechnet"}

        x_loesung_addition = -p / 2 + sp.sqrt(diskriminante)
        x_loesung_subtraktion = -p / 2 - sp.sqrt(diskriminante)

        schritte.append({
            "text": "Berechnung der Lösungen:",
            "latex": f"x_1 = -\\frac{{p}}{{2}} + \\sqrt{{\\Delta}} = -\\frac{{{p}}}{{2}} + \\sqrt{{{sp.latex(diskriminante)}}} = {sp.latex(x_loesung_addition)}"
        })
        schritte.append({
            "text": "Berechnung der Lösungen:",
            "latex": f"x_2 = -\\frac{{p}}{{2}} - \\sqrt{{\\Delta}} = -\\frac{{{p}}}{{2}} - \\sqrt{{{sp.latex(diskriminante)}}} = {sp.latex(x_loesung_subtraktion)}"
        })

        return {
            "schritte": schritte,
            "loesungen": {"x1": x_loesung_addition, "x2": x_loesung_subtraktion}
        }

    def polynomdivision_latex(self, divisor=None):
        """Performs polynomial division and returns LaTeX code (for polynom package)."""
        if divisor is None:
            solutions = sp.solve(self.funktion, self.variable)
            reelle_loesungen = [sol for sol in solutions if sol.is_real]
            if not reelle_loesungen:
                return {"latex": None, "error": "Keine reelle Nullstelle gefunden für die Division."}
            random_solution = random.choice(reelle_loesungen)
            divisor = self.variable - random_solution

        # LaTeX-Code für Polynomdivision erstellen
        dividend_latex = sp.latex(self.funktion)
        divisor_latex = sp.latex(divisor)

        latex_code = f"\\polylongdiv{{{dividend_latex}}}{{{divisor_latex}}}"
        return {"latex": latex_code}


    def polynomdivision(self, divisor=None):
        """Performs step-by-step polynomial division and returns all steps."""
        schritte = []  

        if divisor is None:
            solutions = sp.solve(self.funktion, self.variable)
            reelle_loesungen = [sol for sol in solutions if sol.is_real]
            if not reelle_loesungen:
                return {"schritte": [], "fehler": "Keine reelle Nullstelle gefunden für die Division."}
            random_solution = random.choice(reelle_loesungen)
            divisor = self.variable - random_solution  

        if divisor == 0:
            return {"schritte": [], "fehler": "Fehler: Der Divisor darf nicht 0 sein."}

        schritte.append({
            "text": "Initiale Bedingungen",
            "latex": f"\\text{{Dividend: }} {sp.latex(self.funktion)}, \\text{{ Divisor: }} {sp.latex(divisor)}"
        })

        # Initialer Dividend
        dividend = self.funktion
        quotient = 0  # Gesamter Quotient

        while True:
            try:
                dividend_poly = sp.Poly(dividend, self.variable)
                divisor_poly = sp.Poly(divisor, self.variable)
            except sp.PolynomialError:
                schritte.append({
                    "text": "Fehler: Ungültiges Polynom gefunden.",
                    "latex": "\\text{Division abgebrochen}"
                })
                break

            if dividend_poly.degree() < divisor_poly.degree():
                break 

            lead_dividend = dividend_poly.coeffs()[0]  # Führender Koeffizient
            lead_divisor = divisor_poly.coeffs()[0]  # Führender Koeffizient des Divisors
            monomial_quotient = lead_dividend / lead_divisor * self.variable ** (
                    dividend_poly.degree() - divisor_poly.degree()
            )

            schritte.append({
                "text": f"Berechne Monomial-Quotient für den Dividenden {sp.latex(dividend)}",
                "latex": f"\\text{{Monomial-Quotient: }} {sp.latex(monomial_quotient)}"
            })


            new_dividend = dividend - monomial_quotient * divisor
            schritte.append({
                "text": f"Subtrahiere {sp.latex(monomial_quotient * divisor)} von {sp.latex(dividend)}",
                "latex": f"{sp.latex(dividend)} - ({sp.latex(monomial_quotient)} \\cdot {sp.latex(divisor)}) = {sp.latex(new_dividend)}"
            })


            dividend = sp.simplify(new_dividend)
            quotient += monomial_quotient

            if dividend.is_constant():
                schritte.append({
                    "text": "Dividend ist konstant. Division abgeschlossen.",
                    "latex": f"\\text{{Rest: }} {sp.latex(dividend)}"
                })
                break

        schritte.append({
            "text": "Endergebnis der Polynomdivision",
            "latex": f"\\text{{Quotient: }} {sp.latex(sp.simplify(quotient))}, \\text{{ Rest: }} {sp.latex(dividend)}"
        })

        return {
            "schritte": schritte,
            "end_quotient": quotient,  # Symbolischer Ausdruck für weitere Verarbeitung
            "end_rest": dividend  # Symbolischer Ausdruck für weitere Verarbeitung
        }

    def welche_rechnung_benutzen(self):
        """Selects the appropriate solving method based on polynomial degree."""
        if self.ordnung == 1:
            loesung = sp.solve(self.funktion, self.variable)
            return {
                'Lösungsmethode': 'Lineare Gleichung',
                'Rechenweg': f"\\text{{Setze }} f(x) = 0 \\text{{ und löse: }} x = {', '.join(map(str, loesung))}",
                'LaTeX': f"x = {', '.join(map(sp.latex, loesung))}"
            }

        elif self.ordnung == 2:
            loesung = self.pq_formel()
            rechenweg_schritte = ''.join([step["latex"] for step in loesung["schritte"]])
            return {
                'Lösungsmethode': 'p-q-Formel',
                'Rechenweg': rechenweg_schritte,
                'LaTeX': f"x_1 = {sp.latex(loesung['loesungen']['x1'])}, x_2 = {sp.latex(loesung['loesungen']['x2'])}"
            }

        elif self.ordnung > 2:
            divisionsergebnis = self.polynomdivision_latex()
            if divisionsergebnis.get("error"):
                return {
                    'Lösungsmethode': 'Polynomdivision',
                    'Rechenweg': divisionsergebnis["error"],
                    'LaTeX': ''
                }
            return {
                'Lösungsmethode': 'Polynomdivision',
                'Rechenweg': f"\\text{{Führe Polynomdivision durch: }} {divisionsergebnis['latex']}",
                'LaTeX': divisionsergebnis['latex']
            }

        else:
            return {
                'Lösungsmethode': 'Unbekannte Methode',
                'Rechenweg': 'Die Funktion konnte nicht analysiert werden.',
                'LaTeX': ''
            }

    def vereinfachen(self):
        """Simplifies the given function."""
        try:
            vereinfachte_funktion = sp.simplify(self.funktion)
            return {'Original': self.funktion, 'Vereinfacht': vereinfachte_funktion}
        except Exception as e:
            return f"Fehler bei der Vereinfachung: {e}"

    def format_polynomdivision_as_latex(dividend, divisor, steps):
        """Formats all polynomial division steps as LaTeX table."""
        latex = []
        latex.append(f"\\text{{Dividend: }} {sp.latex(dividend)}, \\text{{ Divisor: }} {sp.latex(divisor)}")
        latex.append("\\begin{array}{r|l}")

        for step in steps:
            # Füge jeden Schritt als LaTeX-Zeile hinzu
            text = step.get("text", "")
            latex_part = step.get("latex", "")
            if text and latex_part:
                latex.append(f"\\text{{{text}}} & {latex_part} \\\\")

        latex.append("\\end{array}")
        return "\n".join(latex)

    def generate_polynom_latex(self, dividend, divisor):
        """Generates complete LaTeX code to render the polynomial division using the polynom package."""
        return f"""
        \\documentclass{{article}}
        \\usepackage{{polynom}}
        \\begin{{document}}
        \\polylongdiv{{{dividend}}}{{{divisor}}}
        \\end{{document}}
        """

    def compile_latex(self, latex_code, output_dir):
        """Compiles LaTeX code into a PDF file."""
        tex_file_path = os.path.join(output_dir, "polynom.tex")
        pdf_file_path = os.path.join(output_dir, "polynom.pdf")

        with open(tex_file_path, "w") as tex_file:
            tex_file.write(latex_code)

        subprocess.run(
            ["pdflatex", "-output-directory", output_dir, tex_file_path],
            check=True
        )
        return pdf_file_path
