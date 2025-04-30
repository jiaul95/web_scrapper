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


# def extract_contact_info(url, tags, conn):
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=True)
#         page = browser.new_page()
#         page.goto(url)
#         page.wait_for_load_state("domcontentloaded")

#         company_name = None
#         email = None
#         phone = None

#         for tag in tags:
#             elements = page.locator(tag)
#             count = elements.count()
#             for i in range(count):
#                 text = elements.nth(i).inner_text().strip()
#                 if not company_name and text:
#                     company_name = text
#                 if not email:
#                     email_elements = page.locator("a[href^='mailto']")
#                     if email_elements.count() > 0:
#                         email = email_elements.nth(0).inner_text().strip()
#                 if not phone:
#                     phone_elements = page.locator("a[href^='tel']")
#                     if phone_elements.count() > 0:
#                         phone = phone_elements.nth(0).inner_text().strip()
#                 if company_name and email and phone:
#                     break
#             if company_name and email and phone:
#                 break

#         if company_name and email and phone:
#             save_to_db(conn, company_name, email, phone)
#         else:
#             print("Could not extract all required information.")

#         browser.close()


def extract_contact_info(url, tags, conn):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print(f"Opening URL: {url}")
        page.goto(url)
        page.wait_for_load_state("domcontentloaded")
        time.sleep(2)

        # Initialize variables
        company_name = None
        phone = None
        email = None  # Email might not be found; we keep it None

        # Attempt to find company name using a specific selector
        try:
            company_name_element = page.locator("h3.moHeading").first
            count = company_name_element.count()
            print(f"Company name elements found: {count}")
            if count > 0:
                company_name = company_name_element.inner_text().strip()
                print(f"Extracted company name: {company_name}")
        except Exception as e:
            print("Error extracting company name:", e)

        # Attempt to find phone number using the specific <p> tag with class
        try:
            phone_element = page.locator("a[href^='tel']").first
            count = phone_element.count()
            print(f"Phone number elements found: {count}")
            if count > 0:
                tel_href = phone_element.get_attribute("href")
                phone = tel_href.replace("tel:", "").strip()
                print(f"Extracted phone: {phone}")
        except Exception as e:
            print("Error extracting phone number:", e)

        if company_name and phone:
            save_to_db(conn, company_name, email, phone)
        else:
            print("Could not extract all required information.")

        browser.close()


if __name__ == "__main__":
    conn = connect_to_db()
    url = input("Enter the website URL: ")
    tags_input = input("Enter the HTML tags to search (comma-separated): ")
    tags = [tag.strip() for tag in tags_input.split(',')]
    extract_contact_info(url, tags, conn)
    conn.close()
