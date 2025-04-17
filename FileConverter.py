import pandas as pd
import json
import os

# Load Excel file
input_file = "UTSA.xlsx"

# Predefined list of semesters (tab names)
semesters_to_process = [
    "2025Spring", "2024Fall", "2024Summer", "2024Spring",
    "2023Fall", "2023Summer", "2023Spring",
    "2022Fall", "2022Summer", "2022Spring"
]

# Load all sheets
xls = pd.ExcelFile(input_file)
sheet_names = xls.sheet_names

# Initialize subjects set
subjects_set = set()

# Sheets to ignore
ignore_sheets = ["Memo", "Data Dictionary and Labels"]

for sheet in semesters_to_process:
    if sheet in ignore_sheets or sheet not in sheet_names:
        continue

    df = pd.read_excel(input_file, sheet_name=sheet, header=None)

    # Check for internal use header
    first_row = str(df.iloc[0, 0]).strip()
    if first_row.upper().startswith("FOR UTSA INTERNAL USE ONLY"):
        df = df.drop(index=0).reset_index(drop=True)

    # Extract column headers and data
    df.columns = df.iloc[0]
    df = df.drop(index=0).reset_index(drop=True)

    # Create NDJSON file per tab
    ndjson_filename = f"{sheet}.ndjson"
    with open(ndjson_filename, "w", encoding='utf-8') as f_out:
        for _, row in df.iterrows():
            row_dict = row.to_dict()
            # Replace NaN with None for JSON compatibility
            row_dict = {k: (None if pd.isna(v) else v) for k, v in row_dict.items()}
            row_dict["tab"] = sheet

            course_val = row_dict.get("Course", None)
            if course_val:
                parts = str(course_val).strip().split(" ")
                if len(parts) == 2:
                    subject_code = parts[0]
                    row_dict["subject"] = subject_code
                    subjects_set.add(subject_code)

            json_line = json.dumps(row_dict)
            f_out.write(json_line + "\n")

# Sort subjects and create subjects dictionary
sorted_subjects = sorted(subjects_set)
subjects_dict = {subject: None for subject in sorted_subjects}

# Write metadata JSON
metadata = {
    "DATA": {
        "SUBJECTS": subjects_dict,
        "SEMESTERS": semesters_to_process
    }
}

metadata_file = "UTSAFees_metadata.json"
with open(metadata_file, "w", encoding='utf-8') as f_meta:
    json.dump(metadata, f_meta, indent=4)

print(f"Converted '{input_file}' to NDJSON files per tab and metadata '{metadata_file}' successfully.")
