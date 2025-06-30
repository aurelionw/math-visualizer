import sympy as sp
import random

class Rechenweg2:

    def __init__(self, funktion, variable):
        self.funktion = funktion
        self.variable = variable

    def polynomdivision(self, divisor=None):
        """
        Führt eine Polynomdivision durch und zeigt die Zwischenschritte an.
        """
        schritte = []  # Liste zur Speicherung der Schritte

        # Falls kein Divisor gegeben ist, versuche, eine reelle Nullstelle zu finden
        if divisor is None:
            solutions = sp.solve(self.funktion, self.variable)
            reelle_loesungen = [sol for sol in solutions if sol.is_real]
            if not reelle_loesungen:
                return "Keine reelle Nullstelle gefunden für die Division."
            random_solution = random.choice(reelle_loesungen)
            divisor = self.variable - random_solution  # Divisor aus Nullstelle

        if divisor == 0:
            return "Fehler: Der Divisor darf nicht 0 sein."

        print(f"Initialer Dividend: {self.funktion}")
        print(f"Divisor: {divisor}")

        # Initialer Dividend
        dividend = self.funktion
        quotient = 0  # Gesamter Quotient

        while sp.Poly(dividend, self.variable).degree() >= sp.Poly(divisor, self.variable).degree():
            if dividend == 0:
                print("Dividend ist 0. Die Division ist abgeschlossen.")
                break

            # Überprüfen, ob `dividend` ein konstantes Polynom geworden ist
            if sp.Poly(dividend, self.variable).degree() == 0:
                print("Konstanter Dividend. Keine weiteren Schritte notwendig.")
                break

            lead_dividend = sp.Poly(dividend, self.variable).LC()  # Führender Koeffizient
            lead_divisor = sp.Poly(divisor, self.variable).LC()  # Führender Koeffizient des Divisors
            monomial_quotient = lead_dividend / lead_divisor * self.variable ** (
                    sp.Poly(dividend, self.variable).degree() - sp.Poly(divisor, self.variable).degree()
            )

            print(f"Aktueller Dividend: {dividend}")
            print(f"Aktueller Divisor: {divisor}")
            print(f"Berechneter Monom-Quotient: {monomial_quotient}")

            # Subtrahiere das Produkt aus Quotient und Divisor vom Dividend
            new_dividend = dividend - monomial_quotient * divisor
            print(f"Neuer Dividend nach Subtraktion: {new_dividend}")

            # Abbruchbedingung bei wiederholtem Dividend
            if sp.simplify(new_dividend) == sp.simplify(dividend):
                print("Keine weitere Reduktion möglich. Division wird abgebrochen.")
                break

            # Speichere den Schritt
            schritte.append({
                'dividend': sp.latex(dividend),
                'divisor': sp.latex(divisor),
                'quotient': sp.latex(monomial_quotient),
                'rest': sp.latex(new_dividend)
            })

            # Aktualisiere den Dividend
            dividend = sp.simplify(new_dividend)
            # Addiere den Monom-Quotient zum Gesamten
            quotient += monomial_quotient

        # Rückgabe der Ergebnisse
        return {
            'schritte': schritte,
            'end_quotient': sp.latex(sp.simplify(quotient)),
            'end_rest': sp.latex(dividend)
        }

    def pq_formel(self):
        """Führt die pq-Formel durch und gibt die Zwischenschritte in LaTeX zurück."""
        funktion_als_liste = sp.Poly(self.funktion).all_coeffs()
        schritte = []  # Liste zur Speicherung der Schritte für die Webseite

        # Abfrage, ob das erste Element in der Liste Vorfaktor 1 besitzt
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

        # Überprüfung ob Ausdruck im Bruch < 0 ist
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


# Beispielanwendung
x = sp.symbols('x')
funktion = x**3 - 3*x + 2
test = Rechenweg2(funktion, x)

funktion2 = x**2 + 5*x + 6

test2 = Rechenweg2(funktion2,x)

print(test2.pq_formel())

x = sp.symbols('x')
funktion = x**3 + 6*x**2 + 11*x + 6
test = Rechenweg(funktion, x)

ergebnis = test.welche_rechnung_benutzen()
print(ergebnis)
