document.addEventListener("DOMContentLoaded", () => {
    const checkboxButtons = document.querySelectorAll('.checkbox-button');
    const resultsSection = document.getElementById('results-section');
    const latexContentDiv = document.querySelector(".latex-content");
    const inputField = document.getElementById('funktion');
    const variableSelect = document.getElementById('int-var'); // Auswahlbox für Variablen
    const loadingIndicator = document.getElementById('loading');


    // Setze Beispieleingabe beim Laden
    const exampleFunction = "x^3 - 3x + 2"; // Beispieleingabe
    inputField.value = exampleFunction;

    let timeout = null;

    // Funktion zur MathJax-Darstellung aufrufen
    function renderMath(content) {
        MathJax.startup.promise = MathJax.startup.promise
            .then(() => MathJax.typesetPromise([content]))
            .catch(err => console.error('MathJax Fehler:', err));
    }

    // LaTeX-Darstellung der Beispieleingabe direkt beim Laden
    function renderExampleFunction() {
        latexContentDiv.innerHTML = `\\( f(x) = ${exampleFunction} \\)`; // Unveränderte Darstellung
        renderMath(latexContentDiv);
    }

    renderExampleFunction(); // Beispieleingabe initial rendern

    // Funktion zur Variablenerkennung
    function detectVariables(expression) {
        try {
            const variables = Array.from(new Set(expression.match(/[a-zA-Z]+/g))); // Extrahiert Variablen
            return variables || [];
        } catch (e) {
            return [];
        }
    }

    // Funktion zum Aktualisieren der Variablenauswahl
    function updateVariableSelect(variables) {
        variableSelect.innerHTML = ''; // Leert die Auswahlbox

        if (variables.length === 0) {
            const defaultOption = document.createElement('option');
            defaultOption.value = 'x';
            defaultOption.textContent = 'x (Standard)';
            variableSelect.appendChild(defaultOption);
        } else if (variables.length === 1) {
            const singleOption = document.createElement('option');
            singleOption.value = variables[0];
            singleOption.textContent = `${variables[0]} (Erkannt)`;
            variableSelect.appendChild(singleOption);
        } else {
            variables.forEach(variable => {
                const option = document.createElement('option');
                option.value = variable;
                option.textContent = variable;
                variableSelect.appendChild(option);
            });
        }
    }

    // Echtzeit-Aktualisierung der LaTeX-Darstellung und Variablen
    inputField.addEventListener('input', () => {
        clearTimeout(timeout);
        const funktion = inputField.value;
        if (funktion.trim()) {
            timeout = setTimeout(() => {
                latexContentDiv.innerHTML = `\\( f(x) = ${funktion} \\)`; // Zeigt Eingabe ohne Vereinfachung
                renderMath(latexContentDiv);

                // Variablen aktualisieren
                const variables = detectVariables(funktion);
                updateVariableSelect(variables);
            }, 300);
        } else {
            latexContentDiv.innerText = '';
            updateVariableSelect(['x']); // Standard-Variable 'x'
        }
    });

    // Checkbox-Handling
    checkboxButtons.forEach(button => {
        button.addEventListener('click', () => button.classList.toggle('selected'));
    });

    // Formular-Handler für die Berechnungen
    document.getElementById('form').addEventListener('submit', (event) => {
        event.preventDefault();
        const funktion = inputField.value;
        const selectedVariable = variableSelect.value; // Ausgewählte Variable
        const selectedCheckboxes = Array.from(checkboxButtons)
            .filter(button => button.classList.contains('selected'))
            .map(button => button.getAttribute('data-value'));

        // Ladeanzeige anzeigen
        loadingIndicator.style.display = 'block';
        resultsSection.style.display = 'none'; // Ergebnisbereich verstecken

        // Berechnung starten und Ergebnisse rendern
        fetch('/api/kurvendiskussion', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ funktion, variable: selectedVariable, selected: selectedCheckboxes })
        })
        .then(response => response.json())
        .then(data => {
            renderResults(data, funktion); // Ergebnisse und Funktion rendern
            loadingIndicator.style.display = 'none'; // Ladeanzeige ausblenden
            resultsSection.style.display = 'block'; // Ergebnisbereich anzeigen
        })
        .catch(error => {
            console.error('Fehler beim Abrufen der Daten:', error);
            resultsSection.innerHTML = "<p>Fehler: Die Daten konnten nicht geladen werden.</p>";
            loadingIndicator.style.display = 'none'; // Ladeanzeige ausblenden
        });
    });

    // Rechenweg hinzufügen
    document.getElementById('results-section').addEventListener('click', (event) => {
        if (event.target && event.target.classList.contains('rechenweg-button')) {
            const funktion = inputField.value;
            const selectedVariable = variableSelect.value;

            loadingIndicator.style.display = 'block';

            // Bestimme, welche Ableitung zu verwenden ist, je nachdem, ob es Extremstellen oder Wendepunkte sind
            let selectedFunction = funktion; // Standardmäßig die Eingabefunktion

            // Verwendet die Ableitung basierend auf dem Typ des angeklickten Rechenwegs
            if (event.target.dataset.type === 'extremstellen') {
                // Verwende die erste Ableitung für Extremstellen
                selectedFunction = data.Ableitungen.erste_ableitung; // Verwende erste Ableitung für Extremstellen
            } else if (event.target.dataset.type === 'wendepunkte') {
                // Verwende die zweite Ableitung für Wendepunkte
                selectedFunction = data.Ableitungen.zweite_ableitung; // Verwende zweite Ableitung für Wendepunkte
            }

            fetch('/api/rechenweg', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ funktion:selectedFunction, variable: selectedVariable })
            })
            .then(response => response.json())
            .then(data => {
                appendRechenweg(data); // Rechenweg an die passende Sektion anhängen
                loadingIndicator.style.display = 'none';
            })
            .catch(error => {
                console.error('Fehler beim Abrufen des Rechenwegs:', error);
                loadingIndicator.style.display = 'none';
            });
        }
    });

    function appendRechenweg(data) {
    let rechenwegContainer = document.querySelector('.rechenweg-container');
    if (!rechenwegContainer) {
        rechenwegContainer = document.createElement('div');
        rechenwegContainer.className = 'rechenweg-container';
        resultsSection.appendChild(rechenwegContainer);
    }

    rechenwegContainer.innerHTML = '<h3>Rechenweg</h3>'; // Reset-Inhalt

    if (data.Rechenweg) {
        const latexDiv = document.createElement('div');
        latexDiv.className = 'latex-output';
        latexDiv.innerHTML = `\\[ ${data.Rechenweg} \\]`;
        rechenwegContainer.appendChild(latexDiv);

        MathJax.typesetPromise([latexDiv])
            .then(() => console.log('MathJax rendering completed'))
            .catch(err => console.error('MathJax rendering error:', err));
    }

    if (data.pdf_url) {
        const pdfLink = document.createElement('a');
        pdfLink.href = data.pdf_url;
        pdfLink.target = '_blank';
        pdfLink.textContent = 'Polynomdivision als PDF anzeigen';
        rechenwegContainer.appendChild(pdfLink);
    }
}



    function performPolynomDivision(dividend, divisor) {
    fetch('/api/polynomdivision', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ dividend, divisor })
    })
    .then(response => response.json())
    .then(data => {
        if (data.pdf_url) {
            const pdfLink = document.createElement('a');
            pdfLink.href = data.pdf_url;
            pdfLink.target = '_blank';
            pdfLink.textContent = 'Ergebnis anzeigen';
            document.body.appendChild(pdfLink);
        } else {
            console.error('Fehler:', data.error);
        }
    })
    .catch(error => console.error('Fehler:', error));
}


    // Funktion zum Rendern der Ergebnisse in speziellen Boxen
    function renderResults(data, funktion) {
        const resultContainer = resultsSection.querySelector('.result-container');
        resultContainer.innerHTML = ''; // Ergebnisse zurücksetzen

        const sectionNames = {
            "y-Achsenabschnitt": "y-Achsenabschnitt mit \\( f(0) \\)", // Neue Reihenfolge
            "Nullstellen": "Nullstellen mit \\( f(x) = 0 \\)", // Neue Reihenfolge
            "Extremstellen": "Extremstellen mit \\( f'(x) = 0 \\)",
            "Wendepunkte": "Wendepunkte mit \\( f''(x) = 0 \\)",
            "Verhalten im unendlichen": "Verhalten im Unendlichen"
        };

        const subtitles = {
            "y-Achsenabschnitt": "y-Achsenabschnitt beträgt:",
            "Nullstellen": "Nullstellen gefunden bei:",
            "Extremstellen": "Extrempunkte gefunden bei:",
            "Wendepunkte": "Wendepunkte gefunden bei:",
            "Verhalten im unendlichen": "Grenzwerte im Unendlichen:"
        };

        Object.entries(sectionNames).forEach(([key, title]) => {
            if (data[key]) {
                const detailElement = document.createElement('details');
                const summaryElement = document.createElement('summary');
                summaryElement.innerText = title;
                detailElement.appendChild(summaryElement);

                if ((key === "Nullstellen" || key === "y-Achsenabschnitt") && funktion) {
                    const funktionParagraph = document.createElement('p');
                    funktionParagraph.innerHTML = `\\( f(x) = ${funktion} \\)`; // Zeigt Funktion an
                    funktionParagraph.style.textAlign = "center";
                    detailElement.appendChild(funktionParagraph);
                }

                if (data.Ableitungen) {
                    if (key === "Extremstellen" && data.Ableitungen.erste_ableitung) {
                        const ableitungParagraph = document.createElement('p');
                        ableitungParagraph.innerHTML = `\\( f'(x) = ${data.Ableitungen.erste_ableitung} \\)`;
                        ableitungParagraph.style.textAlign = "center";
                        detailElement.appendChild(ableitungParagraph);
                    } else if (key === "Wendepunkte" && data.Ableitungen.zweite_ableitung) {
                        const ableitungParagraph = document.createElement('p');
                        ableitungParagraph.innerHTML = `\\( f''(x) = ${data.Ableitungen.zweite_ableitung} \\)`;
                        ableitungParagraph.style.textAlign = "center";
                        detailElement.appendChild(ableitungParagraph);
                    }
                }

                const subtitleElement = document.createElement('p');
                subtitleElement.innerText = subtitles[key];
                subtitleElement.style.fontWeight = "bold";
                subtitleElement.style.marginTop = "10px";
                subtitleElement.style.textAlign = "center";
                detailElement.appendChild(subtitleElement);

                const resultsList = document.createElement('ul');
                resultsList.style.listStyleType = "none"; // Entfernt die Punkte
                resultsList.style.padding = "0"; // Entfernt Innenabstand
                resultsList.style.margin = "0 auto"; // Zentriert die Liste
                resultsList.style.textAlign = "center"; // Zentriert die Texte

                const values = Array.isArray(data[key]) ? data[key] : [data[key]];
                values.forEach((value) => {
                    const listItem = document.createElement('li');
                    if (key === "y-Achsenabschnitt") {
                        listItem.innerHTML = `\\( ${value} \\)`;
                    } else {
                        listItem.innerHTML = `\\( x = ${value} \\)`;
                    }
                    listItem.style.display = "inline-block"; // Ergebnisse nebeneinander
                    listItem.style.margin = "0 10px"; // Abstand zwischen Ergebnissen
                    resultsList.appendChild(listItem);
                });

                detailElement.appendChild(resultsList);

                const buttonContainer = document.createElement('div');
                buttonContainer.style.display = "flex";
                buttonContainer.style.justifyContent = "center";
                buttonContainer.style.gap = "10px";
                buttonContainer.style.marginTop = "10px";

                const rechenwegButton = document.createElement('button');
                rechenwegButton.className = 'dynamic-button rechenweg-button';
                rechenwegButton.innerText = 'Rechenweg';
                rechenwegButton.addEventListener('click', () => {
                    const funktion = inputField.value;
                    const selectedVariable = variableSelect.value;

                    fetch('/api/rechenweg', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ funktion, variable: selectedVariable })
                    })
                    .then(response => response.json())
                    .then(data => {
                        console.log("Rechenweg-Daten empfangen", data)
                        appendRechenweg(data); // Aktualisiere den Rechenweg
                    })
                    .catch(error => console.error('Fehler beim Abrufen des Rechenwegs:', error));
                })

                const vereinfachenButton = document.createElement('button');
                vereinfachenButton.className = 'dynamic-button';
                vereinfachenButton.innerText = 'Vereinfachen';

                buttonContainer.appendChild(rechenwegButton);
                buttonContainer.appendChild(vereinfachenButton);
                detailElement.appendChild(buttonContainer);

                resultContainer.appendChild(detailElement);
            }
        });

        

        renderMath(resultContainer);
    }
});
