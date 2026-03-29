# EC-Lab Electrochemical Cells and Supercapacitors Data Analysis

Python tools for parsing, analyzing, and visualizing electrochemical data generated with BioLogic EC-Lab software.

This repository was developed to provide a reproducible workflow for processing battery and electrochemical experiments using Python.

The project focuses on building a modular and extensible analysis pipeline that can be reused for future research and data analysis tasks.

---

# Features

* Parse EC-Lab data files:

  * `.mpr`
  * `.mpt`
  * `.mpl`
  * `.mpp`

* Data analysis for electrochemical experiments:

  * Capacity vs cycle number
  * Coulombic efficiency
  * Voltage profiles
  * Rate capability
  * Basic electrochemical performance metrics

* Automatic plot generation

* Modular Python structure

* Reproducible analysis workflow

* Ragone plot

---

# Project Structure

eclab-analysis/

data/
raw/
processed/

notebooks/
exploration.ipynb

src/
eclab_analysis/
parser.py
analysis.py
plotting.py
utils.py

scripts/
run_analysis.py

results/
figures/
tables/

README.md
requirements.txt

---

# Installation

Clone the repository:

git clone https://github.com/your-username/eclab-analysis.git

cd eclab-analysis

Install dependencies:

pip install -r requirements.txt

---

# Requirements

Python 3.9 or newer.

Main libraries:

* pandas
* numpy
* matplotlib
* scipy
* galvani

Optional:

* jupyter
* seaborn

---

# Usage

Basic example:

python scripts/run_analysis.py data/raw/example.mpt

This will:

* load the data file
* perform the analysis
* generate plots
* save results in the results folder

---

# Supported Experiments

The analysis tools are designed for typical electrochemical experiments:

Battery cycling
Galvanostatic charge/discharge
Rate capability tests
Cyclic voltammetry
Electrochemical impedance spectroscopy

The workflow can be extended to other electrochemical systems.

---

# Example Outputs

Typical generated figures:

Capacity vs Cycle
Voltage vs Capacity
Coulombic Efficiency vs Cycle
Rate Capability Plot

All plots are automatically saved in:

results/figures/

---

# Data Processing Workflow

1. Load raw EC-Lab data file
2. Clean and format the dataset
3. Compute electrochemical metrics
4. Generate plots
5. Save processed data and figures

---

# Motivation

Electrochemical experiments often generate large datasets that require systematic processing and visualization.

This project aims to:

* improve reproducibility
* automate repetitive analysis tasks
* create reusable research tools
* build practical data analysis skills for electrochemical energy storage systems

---

# Future Improvements

Possible extensions:

---

# Author

Name: Mattia Gamberini

MSc Automation Engineering

Focus areas:

* too much...

---

# License

/

---

# Contact

For questions or collaboration:

mattia.gamberini53@gmail.com
