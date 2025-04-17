import pandas as pd
from collections import defaultdict
import requests
from bs4 import BeautifulSoup
import os

def scrape_fee_details(urls):
    fee_details = {}
    
    for url in urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        table = soup.find('table', class_='sc_sctable')
        if table:
            rows = table.find_all('tr')[1:]
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 5:
                    fee_name = cols[0].text.strip()
                    fee_code = cols[1].text.strip()
                    fee_desc = cols[4].text.strip()
                    
                    if fee_code:
                        fee_details[fee_code] = (fee_name, fee_desc)
    
    return fee_details

if __name__ == "__main__":
    input_files = {
        "MATH.xlsx": ["2021Fall", "2022Spring", "2022Summer"]        
    }
    # "BIO.xlsx": ["2024Fall", "2025Spring"]
    # "MATH.xlsx": ["2024Fall", "2025Spring"]
    # "MATH.xlsx": ["2023Fall", "2024Spring", "2024Summer"]
    # "MATH.xlsx": ["2022Fall", "2023Spring", "2023Summer"]

    UTSA_FEES_URLS = [
        "https://catalog.utsa.edu/undergraduate/coursefees/",
        "https://catalog.utsa.edu/graduate/coursefees/"
    ]
    fee_details = scrape_fee_details(UTSA_FEES_URLS)

    def compute_section_fees(row):
        fees = defaultdict(int)
        if pd.isna(row['Course Fees']) or pd.isna(row['Actual Enrollment']):
            return fees
        enrollment = int(row['Actual Enrollment'])
        fee_list = str(row['Course Fees']).split(',')
        for fee_str in fee_list:
            fee_code, fee_val = fee_str.strip().split(':')
            fees[fee_code] += round(float(fee_val) * enrollment)
        return fees

    def compute_course_fees(course_fees_list):
        total_fees = defaultdict(int)
        for fees in course_fees_list:
            for fee_code, fee_val in fees.items():
                total_fees[fee_code] += fee_val
        return total_fees

    def compute_accumulated_fees(df):
        accumulated_fees = defaultdict(int)
        for _, row in df.iterrows():
            for fee_code, fee_val in row['Total_Fees'].items():
                accumulated_fees[fee_code] += fee_val
        return accumulated_fees

    def compute_CHPC(row):
        last_digit = int(str(row['Course']).split(" ")[1][3])
        return last_digit * int(row['Actual Enrollment'])

    def process_fees(input_filename, tab_names):
        output_filename = os.path.splitext(input_filename)[0] + "_Results.xlsx"
        all_tabs_accumulated_fees = defaultdict(int)
        total_CHPC = 0
        total_students = 0
        
        with pd.ExcelWriter(output_filename, engine='xlsxwriter') as writer:
            workbook = writer.book
            currency_format = workbook.add_format({'num_format': '$#,##0'})

            # Prepare summary first
            for tab in tab_names:
                df = pd.read_excel(input_filename, sheet_name=tab)

                df['Section_Fees'] = df.apply(compute_section_fees, axis=1)
                df['CHPC'] = df.apply(compute_CHPC, axis=1)
                total_students += df['Actual Enrollment'].sum()

                grouped_df = df.groupby('Course').agg({'Section_Fees': list, 'CHPC': "sum"})
                grouped_df['Total_Fees'] = grouped_df['Section_Fees'].apply(compute_course_fees)

                tab_accumulated_fees = compute_accumulated_fees(grouped_df)
                tab_total_CHPC = grouped_df['CHPC'].sum()
                total_CHPC += tab_total_CHPC

                for fee_code, fee_val in tab_accumulated_fees.items():
                    all_tabs_accumulated_fees[fee_code] += fee_val

                section_fees_df = df[['Course', 'Section_Fees', 'CHPC']]
                total_fees_df = grouped_df[['Total_Fees', 'CHPC']]
                accumulated_fees_df = pd.DataFrame(list(tab_accumulated_fees.items()), columns=["Fee Code", "Total Amount"])

                section_fees_df.to_excel(writer, sheet_name=f"{tab}_Sections", index=False)
                total_fees_df.to_excel(writer, sheet_name=f"{tab}_Courses")
                accumulated_fees_df.to_excel(writer, sheet_name=f"{tab}_Accumulated", index=False)

                worksheet = writer.sheets[f"{tab}_Accumulated"]
                worksheet.set_column('B:B', 15, currency_format)

            # Summary tab written first
            summary_df = pd.DataFrame(list(all_tabs_accumulated_fees.items()), columns=["Fee Code", "Total Amount"])
            summary_df["Fee Name"] = summary_df["Fee Code"].map(lambda code: fee_details.get(code, ("N/A", "N/A"))[0])
            summary_df["Fee Description"] = summary_df["Fee Code"].map(lambda code: fee_details.get(code, ("N/A", "N/A"))[1])
            summary_df = summary_df[['Fee Code', 'Fee Name', 'Total Amount', 'Fee Description']]

            summary_totals = pd.DataFrame(
                [["Total Credit Hours", total_CHPC], ["Total Seats", total_students]], 
                columns=["Metric", "Value"]
            )

            summary_df.to_excel(writer, sheet_name="Summary", index=False)
            summary_totals.to_excel(writer, sheet_name="Summary", startrow=len(summary_df) + 2, startcol=0, index=False)
            summary_worksheet = writer.sheets["Summary"]
            summary_worksheet.set_column('C:C', 15, currency_format)

        print(f"Results saved to {output_filename}")

    for filename, tabs in input_files.items():
        process_fees(filename, tabs)
