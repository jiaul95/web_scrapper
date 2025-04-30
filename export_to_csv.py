import sqlite3
import csv

def export_to_csv():
    conn = sqlite3.connect('distributors.db')
    c = conn.cursor()
    c.execute("SELECT company_name, email, phone FROM companies")
    rows = c.fetchall()
    with open('companies.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Company Name', 'Email', 'Phone'])
        writer.writerows(rows)
    conn.close()

if __name__ == "__main__":
    export_to_csv()
