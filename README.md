# UTSA Course Fees Dashboard

This project provides a data processing pipeline and interactive visualization tool for analyzing course fees at the University of Texas at San Antonio (UTSA). It includes Python scripts for data conversion and aggregation, and a web-based interface for visual analysis.

## Components

### 1. `FileConverter.py`
This Python script converts Excel spreadsheets containing course data into structured, newline-delimited JSON (NDJSON) files.

**Inputs:**
- A file named `UTSA.xlsx` containing multiple semester tabs.

**Outputs:**
- A `.ndjson` file for each semester listed in the script.
- A metadata file `UTSAFees_metadata.json` listing available subjects and semesters.

**Key Features:**
- Ignores header rows marked for internal use.
- Extracts subject codes from the "Course" column.
- Replaces invalid JSON values like `NaN` with `null`.
- Supports pre-defined semester tab names.

### 2. `CourseFees.py`
This Python script reads `UTSA.xlsx` and computes aggregated fee data per course and per subject.

**Functionality:**
- Reads tabs from an Excel file and computes:
  - Fee amounts by course section
  - Aggregated totals by course and subject
  - Credit hours per course (based on course number)
- Exports the results into a structured Excel file with:
  - Per-semester summaries
  - A comprehensive summary tab
  - Formatted totals using currency styling

**Output File:**
- `CourseSchedule_Results.xlsx` (or a similar name depending on the input file)

## Web Application (`UTSAFees.html`)
- Displays interactive controls for semester and subject selection
- Shows tables and pie charts of fee totals
- Includes export functionality for summary data
- Displays time series plots for selected fees across semesters

## How to Use
1. Place the input file `UTSA.xlsx` in the working directory.
2. Run `FileConverter.py` to generate NDJSON files.
3. Open `UTSAFees.html` in a web browser hosted via a local or public web server.
4. Optionally, run `CourseFees.py` to produce a summarized Excel report.

## Requirements
- Python 3.x
- pandas, openpyxl, xlsxwriter
- A web server (e.g., Python's `http.server`, IIS, Apache) for serving the HTML interface

## License
MIT License

---
For more information about course fees at UTSA, visit:
- [Undergraduate Course Fees](https://catalog.utsa.edu/undergraduate/coursefees/)
- [Graduate Course Fees](https://catalog.utsa.edu/graduate/coursefees/)
- [Tuition and Fees Policy](https://catalog.utsa.edu/policies/tuitionfees/tuition/)

