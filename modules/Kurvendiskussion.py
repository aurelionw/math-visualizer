import sympy as sp
import matplotlib.pyplot as plt
import numpy as np

class Kurvendiskussion:
    def __init__(self, funktion, variable):
        #Funktion und Variablen initialisieren
        self.funktion = funktion
        self.variable = variable
        self.erste_ableitung = None
        self.zweite_ableitung = None
        self.dritte_ableitung = None


#------------ SCHNITTPUNKT MIT KOORDINATENACHSE ------------
    #x-Achsenschnittpunkte
    def nullstellen(self):
        nullstellen = sp.solve(self.funktion, self.variable)
        return {'Nullstellen' : nullstellen}



    #Y-Achsenabschnitt
    def berechne_y_achsenabschnitt(self):
        y_achsenabschnitt = self.funktion.subs(self.variable,0) #berechnet den y-Achsenabschnitt
        return {'y-Achsenabschnitt': [y_achsenabschnitt]}


#------------ ABLEITUNGEN ------------
    def berechne_erste_ableitung(self):
        if self.erste_ableitung is None:
            self.erste_ableitung = sp.diff(self.funktion,self.variable)
        return self.erste_ableitung

    def berechne_zweite_ableitung(self):
        if self.zweite_ableitung is None:
            self.zweite_ableitung = sp.diff(self.funktion,self.variable,2)
        return self.zweite_ableitung

    def berechne_dritte_ableitung(self):
        if self.dritte_ableitung is None:
            self.dritte_ableitung = sp.diff(self.funktion,self.variable,3)
        return self.dritte_ableitung

    def ableitungen_anzeigen(self, welche_ableitungen):
        ableitungen = {}
        if 'erste' in welche_ableitungen:
            ableitungen['erste_ableitung'] = sp.latex(self.berechne_erste_ableitung())
        if 'zweite' in welche_ableitungen:
            ableitungen['zweite_ableitung'] = sp.latex(self.berechne_zweite_ableitung())
        if 'dritte' in welche_ableitungen:
            ableitungen['dritte_ableitung'] = sp.latex(self.berechne_dritte_ableitung())
        return ableitungen

#------------ EXTREMPUNKTE ------------

#Extremstellen - notwendige Bedingung

    def berechne_extremstellen(self):
        # Stelle sicher, dass die erste Ableitung berechnet wurde
        if self.erste_ableitung is None:
            self.berechne_erste_ableitung()  # Berechnet die erste Ableitung

        # Finde die Nullstellen der ersten Ableitung
        extremstellen = sp.solve(self.erste_ableitung, self.variable)
        return {'extremstellen': extremstellen}



#hinreichende Bedingung
    def hinreichende_bedingung_extremstellen(self):
        # Berechne die Extremstellen (Nullstellen der ersten Ableitung)
        extremstellen = self.berechne_extremstellen()
        extremstellen = [*extremstellen.values()][0]

        # Initialisiere leere Listen für Minima, Maxima und Sattelpunkte
        minima = []
        maxima = []
        sattelpunkte = []
        # Stelle sicher, dass die zweite Ableitung berechnet wurde
        if self.zweite_ableitung is None:
            self.berechne_zweite_ableitung()


        for punkt in extremstellen:
            wert_zweite_ableitung = self.zweite_ableitung.subs(self.variable, punkt)

            # Hier die entsprechenden Punkte in die Listen einfügen
            if wert_zweite_ableitung > 0:
                minima.append(punkt)
            elif wert_zweite_ableitung < 0:
                maxima.append(punkt)
            else:
                sattelpunkte.append(punkt)

            # Rückgabe als Dictionary für eine klare Struktur
        return {
            "Minima": minima,
            "Maxima": maxima,
            "Sattelpunkte": sattelpunkte
        }


#------------ WENDEPUNKTE ------------

#notwendige Bedingung
    def berechne_wendepunkte(self):
        # Stelle sicher, dass die erste Ableitung berechnet wurde
        if self.zweite_ableitung is None:
            self.berechne_zweite_ableitung()  # Berechnet die zweite Ableitung

        # Finde die Nullstellen der zweiten Ableitung
        wendepunkte = sp.solve(self.zweite_ableitung, self.variable)
        return {'wendepunkte': wendepunkte}

#hinreichende Bedingung
    def hinreichende_bedingung_wendepunkte(self):
        # Berechne die Wendepunkte (Nullstellen der zweiten Ableitung)
        wendepunkte = self.berechne_wendepunkte()
        wendepunkte = [*wendepunkte.values()][0]

        rl_kruemmung = []
        lr_kruemmung = []
        keine_aussage = []


        # Stelle sicher, dass die dritte Ableitung berechnet wurde
        if self.dritte_ableitung is None:
            self.berechne_dritte_ableitung()

        # Klassifizierung der Wendepunkte als Dictionary
        klassifikation_wendepunkt = {}

        for punkt in wendepunkte:
            wert_zweite_ableitung = self.dritte_ableitung.subs(self.variable, punkt)

            # Hier die entsprechenden Punkte in die Listen einfügen
            if wert_zweite_ableitung > 0:
                rl_kruemmung.append(punkt)
            elif wert_zweite_ableitung < 0:
                lr_kruemmung.append(punkt)
            else:
                keine_aussage.append(punkt)

            # Rückgabe als Dictionary für eine klare Struktur
        return {
            "Rinks-Rechts-Krümmung": rl_kruemmung,
            "Links-Rechtskrümmung": lr_kruemmung,
            "Keine Aussage": keine_aussage
        }





#------------ ZUSÄTZLICHE SACHEN ------------

    """Vereinfachte Darstellung der Funktion"""
    def vereinfachte_funktion(self):
        vereinfachte_darstellung = sp.simplify(self.funktion)
        if vereinfachte_darstellung == self.funktion:
            return {'simplified': vereinfachte_darstellung }
        else:
            return{'simplified': None}


#------------ SYMMETRIEEIGENSCHAFTEN ------------

    """Symmetrie-Eigenschaften"""
    def symmetrie_eigenschaft(self):
        symmetrie_eigenschaft = self.funktion.subs(self.variable, - self.variable)
        antwort_symmetrie = {}
        if self.funktion == symmetrie_eigenschaft:
            antwort_symmetrie['Symmetrie-Eigenschaft'] = 'achsensymmetrisch'
            #print("Die Funktion ist achsensymmetrisch bezüglich der y-Achse")
        elif self.funktion == - symmetrie_eigenschaft:
            antwort_symmetrie['Symmetrie-Eigenschaft'] = 'punktsymmetrisch'
            #print("Die Funktion ist punktsymmetrisch bezüglich des Ursprungs")
        else:
            #print("Die Funktion weder Achsen- noch Punktsymmetrisch")
            antwort_symmetrie['Symmetrie-Eigenschaft'] = 'weder achsen- noch punktsymmetrisch'

        return antwort_symmetrie        #Wiedergabe der Symmetrie-Eigenschaft mit key 'Symmetrie-Eigenschaft'


#------------ POLSTELLEN ------------

    def ist_es_ein_bruch(self):
        zaehler, nenner = self.funktion.as_numer_denom()
        if nenner.has(self.variable):
            return nenner
        return None  # Klarheit, dass es kein Bruch ist

    def finde_polstellen(self):
        nenner = self.ist_es_ein_bruch()

        #Überprüfung, ob es sich um einen Bruch handelt
        if nenner is None:
            return {}  # Gibt ein leeres Dictionary zurück

        polstellen = sp.solve(nenner, self.variable)
        return {'Polstellen' : polstellen}

#------------ VERHALTEN IM UNENDLICHEN ------------
    def verhalten_im_unendlichen(self):
        limit_negativ = sp.limit(self.funktion,self.variable,-sp.oo)
        limit_positiv = sp.limit(self.funktion, self.variable,sp.oo)

        #Speichern der Grenzwerte im dictionary
        Grenzwerte = {}

        if limit_negativ != limit_positiv:
            Grenzwerte['positiv_unendlich'] = limit_positiv
            Grenzwerte['negativ_unendlich'] = limit_negativ
        else:
            Grenzwerte['Grenzwert'] = limit_positiv

        return Grenzwerte

#------------ PLOT ------------
    def plot_der_funktion(self):
        # Funktion lambdifizieren
        f_lambdify = sp.lambdify(self.variable, self.funktion, 'numpy')

        # Nullstellen, Extremstellen und Wendepunkte berechnen
        nullstellen_dict = self.nullstellen()
        extremstellen_dict = self.hinreichende_bedingung_extremstellen()
        wendepunkte_dict = self.hinreichende_bedingung_wendepunkte()


        # Werte aus Dictionaries extrahieren und in eine Liste konvertieren
        if nullstellen_dict:
            nullstellen = nullstellen_dict.get("Nullstellen", [])
        else:
            nullstellen_dict = []
        if extremstellen_dict:
            extremstellen = [wert for werte in extremstellen_dict.values() for wert in werte]
        else:
            extremstellen = []

        if wendepunkte_dict:
            wendepunkte = [wert for werte in wendepunkte_dict.values() for wert in werte]
        else:
            wendepunkte = []



        # Wichtige Punkte extrahieren und in eine Liste packen
        wichtige_punkte = nullstellen + extremstellen + wendepunkte
        wichtige_punkte = [float(p) for p in wichtige_punkte if p.is_real]

        # Dynamischen Plotbereich berechnen
        if wichtige_punkte:
            x_min = min(wichtige_punkte) - 1  # Puffer von 1 Einheiten
            x_max = max(wichtige_punkte) + 1
        else:
            x_min, x_max = -10, 10  # Standardbereich, falls keine Punkte vorhanden



        # X-Wertebereich basierend auf Grenzen anpassen
        x_vals = np.linspace(x_min, x_max, 1000)
        y_vals = f_lambdify(x_vals)

        # Berechnung der y-Achsenlimits
        y_min = min(y_vals)
        y_max = max(y_vals)

        # Punkte plotten
        if nullstellen:
            plt.scatter(nullstellen, [f_lambdify(float(ns)) for ns in nullstellen], color='red', label='Nullstellen',
                        zorder=5)
        if extremstellen:
            plt.scatter(extremstellen, [f_lambdify(float(es)) for es in extremstellen], color='green',
                        label='Extremstellen', zorder=5)
        if wendepunkte:
            plt.scatter(wendepunkte, [f_lambdify(float(wp)) for wp in wendepunkte], color='blue', label='Wendepunkte',
                        zorder=5)


        # Achsenlimits setzen
        plt.xlim(x_min, x_max)
        plt.ylim(y_min - 2, y_max + 2)  # Puffer für die y-Achse


        # Plot erstellen
        plt.plot(x_vals, y_vals, label=str(self.funktion))
        plt.title("Plot der Funktion")
        plt.xlabel("x")
        plt.ylabel("f(x)")
        plt.axhline(0, color='black', linewidth=0.5)
        plt.axvline(0, color='black', linewidth=0.5)
        plt.legend()
        plt.grid(True)
        plt.show()




x = sp.symbols('x')

funktion = x**3 - 3*x**2 + 2  # Definiere die Funktion
#funktion2 = (x+1)*(x+3)
#funktion3 = x**2
#funktion4 = (x**2 + 3*x + 2) / (1-x**2)


# Erstelle eine Instanz der Klasse
kurve = Kurvendiskussion(funktion, x)
#print(kurve.berechne_extremstellen())
kurve.plot_der_funktion()
#print(kurve.berechne_y_achsenabschnitt())
#kurve.ausgabe_extremstellen()
#print(kurve.hinreichende_bedingung_extremstellen())
#print(kurve.hinreichende_bedingung_wendepunkte())
#print("polstellen")
#print(kurve.finde_polstellen())
#print(kurve.verhalten_im_unendlichen())
#print(kurve.symmetrie_eigenschaft())
#print()

