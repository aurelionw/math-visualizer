# Math Visualizer – Web-Based Function Analysis Tool

This repository contains a web application for interactive function analysis, including zero-crossings, extrema, inflection points, and end behavior. The tool is primarily aimed at educational and mathematical purposes.

## Features

- Detects and plots:
  - Zeros (roots)
  - First and second derivatives
  - Extrema (minima/maxima)
  - Inflection points
  - Asymptotic/end behavior
  - Symmetry properties
- Automatic curve sketching using `matplotlib`
- Step-by-step explanations in LaTeX (e.g., PQ formula, polynomial division)
- Interactive web interface using Flask, JavaScript, and MathJax

## Tech Stack

- **Backend:** Python, Flask, SymPy, NumPy
- **Frontend:** HTML, CSS, JavaScript, MathJax
- **Visualization:** `matplotlib`, LaTeX (for rendering equations)
- **Web Server:** Flask App

## How to Run Locally

```bash
git clone https://github.com/aurelionw/math-visualizer.git
cd math-visualizer
pip install -r requirements.txt
python app.py

Then open your browser and go to:
http://127.0.0.1:5000/

## Author

Aurélio Nwamusse  
[GitHub Profile](https://github.com/aurelionw)

## Disclaimer

This tool is intended for educational use only. Please verify results in academic or professional contexts.
