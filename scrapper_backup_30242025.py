from db_setup import connect_to_db
from playwright.sync_api import sync_playwright
import time

def save_to_db(conn, company_name, email, phone):
    try:
        cursor = conn.cursor()
        insert_query = """
            INSERT INTO distributors_contacts (company_name, email, phone)
            VALUES (%s, %s, %s)
        """
        cursor.execute(insert_query, (company_name, email, phone))
        conn.commit()
        print("Data inserted successfully.")
    except Exception as e:
        print(f"Error inserting data: {e}")

# def extract_multiple_contacts(url, tags, conn):
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=True)
#         page = browser.new_page()
#         print(f"Opening URL: {url}")
#         page.goto(url)
#         page.wait_for_load_state("domcontentloaded")
#         time.sleep(2)

#         # Locate all company blocks
#         company_blocks = page.locator("div.col-6.col-md-3.custom-margin")
#         count = company_blocks.count()
#         print(f"Total company blocks found: {count}")

#         for i in range(count):
#             block = company_blocks.nth(i)
            
#             try:
#                 # Extract company name
#                 company_name = block.locator("h3.moHeading").inner_text().strip()
#             except Exception as e:
#                 print(f"Error extracting company name for block {i+1}: {e}")
#                 company_name = None

#             try:
#                 # Extract phone number
#                 phone = block.locator("a[href^='tel']").get_attribute("href")
#                 if phone:
#                     phone = phone.replace("tel:", "").strip()
#             except Exception as e:
#                 print(f"Error extracting phone number for block {i+1}: {e}")
#                 phone = None

#             # Email not present in list page, optional
#             email = None

#             print(f"{i+1}. Company: {company_name}, Phone: {phone}")

#             # Decide whether to skip or stop processing
#             if not company_name and not phone:
#                 print(f"No company name and phone found for block {i+1}. Stopping the loop.")
#                 break  # Stop processing further if both are missing

#             if company_name and phone:
#                 save_to_db(conn, company_name, email, phone)
#             else:
#                 print(f"Skipping entry {i+1}: Missing company name or phone.")

#         browser.close()


def extract_multiple_contacts(url, tags, conn):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print(f"Opening URL: {url}")
        page.goto(url)
        page.wait_for_load_state("domcontentloaded")
        time.sleep(3)

        # Click "View More" repeatedly until it's gone
        while True:
            try:
                view_more_button = page.locator("div.more-cat-link p:has-text('View More')")

                if view_more_button.is_visible():
                    print("Clicking 'View More' button...")
                    view_more_button.click()
                    time.sleep(2)  # Wait for more data to load
                else:
                    print("'View More' button not visible anymore.")
                    break
            except Exception as e:
                print(f"Error clicking 'View More': {e}")
                break

        # Now scrape all loaded company blocks
        company_blocks = page.locator("div.col-6.col-md-3.custom-margin")
        count = company_blocks.count()
        print(f"Total company blocks found: {count}")

        for i in range(count):
            block = company_blocks.nth(i)
            
            try:
                company_name = block.locator("h3.moHeading").inner_text().strip()
            except Exception as e:
                print(f"Error extracting company name for block {i+1}: {e}")
                company_name = None

            try:
                phone = block.locator("a[href^='tel']").get_attribute("href")
                if phone:
                    phone = phone.replace("tel:", "").strip()
            except Exception as e:
                print(f"Error extracting phone number for block {i+1}: {e}")
                phone = None

            email = None  # Email is optional or missing

            print(f"{i+1}. Company: {company_name}, Phone: {phone}")

            if not company_name and not phone:
                print(f"No company name and phone found for block {i+1}. Stopping the loop.")
                break

            if company_name and phone:
                save_to_db(conn, company_name, email, phone)
            else:
                print(f"Skipping entry {i+1}: Missing company name or phone.")

        browser.close()


if __name__ == "__main__":
    conn = connect_to_db()
    url = input("Enter the website URL: ")
    tags_input = input("Enter the HTML tags to search (comma-separated): ")
    tags = [tag.strip() for tag in tags_input.split(',')]
    extract_multiple_contacts(url, tags, conn)
    conn.close()
