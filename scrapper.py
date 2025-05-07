from db_setup import connect_to_db
from playwright.sync_api import sync_playwright
import time
from itertools import zip_longest

def save_to_db(conn, company_name, email, phone,url):
    try:
        cursor = conn.cursor()
        insert_query = """
            INSERT INTO distributors_contacts (company_url,company_name, email, phone)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (url,company_name, email, phone))
        conn.commit()
        print("Data inserted successfully.")
    except Exception as e:
        print(f"Error inserting data: {e}")


def extract_value(block, selector, attr='text'):
    values = []  # List to store values
    try:
        locator = block.locator(selector)
        count = locator.count()
        if count > 0:
            for i in range(count):
                el = locator.nth(i)
                if attr == 'href':
                    values.append(el.get_attribute('href').strip())
                else:
                    values.append(el.inner_text().strip())
    except Exception as e:
        print(f"Error extracting value for selector {selector}: {e}")
    return values  # Return a list of values


def extract_contact_from_page(page):
    # This function extracts phone and email from an individual company's page.
    phones = extract_value(page, "a[href^='tel']")
    emails = extract_value(page, "a[href^='mailto']")
    return phones, emails

def extract_multiple_contacts(url, conn, block_selector=None):
    block_selector = block_selector
    print(f"block_selector: {block_selector}")


    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        # print(f"Opening URL: {url}")
        page.goto(url,timeout=60000)
        page.wait_for_load_state("domcontentloaded")
        time.sleep(3)

        # try:
        #     while True:
        #         view_more_button = page.locator("div.more-cat-link p:has-text('View More')")
        #         if view_more_button and view_more_button.is_visible():
        #             print("Clicking 'View More' button...")
        #             view_more_button.click()
        #             time.sleep(2)
        #         else:
        #             print("'View More' button not found or not visible.")
        #             break
        # except Exception as e:
        #     print(f"No 'View More' found or error occurred: {e}. Proceeding with available content.")

        try:
         while True:
                # Try clicking "View More" if available
                view_more_button = page.locator("div.more-cat-link p:has-text('View More')")
                if view_more_button and view_more_button.is_visible():
                    print("Clicking 'View More' button...")
                    view_more_button.click()
                    time.sleep(2)
                    continue  # Try again after expanding

                # Try pagination if "View More" is not found
                next_button = page.locator("a:has-text('Next'), a.pagination-next, button.next, a[rel='next']")
                if next_button and next_button.is_visible():
                    print("Navigating to next page...")
                    next_button.click()
                    page.wait_for_load_state("domcontentloaded")
                    time.sleep(2)
                else:
                    print("No more pages to navigate.")
                    break
        except Exception as e:
            print(f"Pagination ended or error occurred: {e}")

        company_blocks = page.locator(block_selector)
        count = company_blocks.count()

        print(f"company_blocks {company_blocks}")
        print(f"count {count}")      


        if count == 0:
            print("No company blocks found. Extracting single contact from the page.")
            block = page  # Use the full page as a block

            company_names = extract_value(block, "h3, h2, h1")
            phones = extract_value(block, "a[href^='tel']")
            emails = extract_value(block, "a[href^='mailto']")

            for company_name, phone, email in zip_longest(company_names, phones, emails):
                if phone and phone.startswith("tel:"):
                    phone = phone.replace("tel:", "").strip()

                if email and email.startswith("mailto:"):
                    email = email.replace("mailto:", "").strip()

                print(f"Company: {company_name}, Phone: {phone}, Email: {email}")

                if company_name and phone:
                    save_to_db(conn, company_name, email, phone, url)
                else:
                    print("Skipping entry: Missing company name or phone.")
        else:
            print(f"Total company blocks found: {count}")

            for i in range(count):
                block = company_blocks.nth(i)

                company_names = extract_value(block, "h3, h2, h1")
                phones = extract_value(block, "a[href^='tel']")
                emails = extract_value(block, "a[href^='mailto']")

                for company_name, phone, email in zip_longest(company_names, phones, emails):
                    if phone and phone.startswith("tel:"):
                        phone = phone.replace("tel:", "").strip()

                    if email and email.startswith("mailto:"):
                        email = email.replace("mailto:", "").strip()

                    print(f"{i+1}. Company: {company_name}, Phone: {phone}, Email: {email}")

                    if company_name and phone:
                        save_to_db(conn, company_name, email, phone)
                    else:
                        print(f"Skipping entry {i+1}: Missing company name or phone.")

        browser.close()

# if __name__ == "__main__":
#     conn = connect_to_db()
#     url = input("Enter the website URL: ")
    
#     block_selector_input = input("Enter the block selector (leave empty to use default): ").strip()

#     extract_multiple_contacts(url, conn, block_selector_input if block_selector_input else None)
#     conn.close()


def normalize_selector(selector_input):
    if not selector_input:
        return None
    selector_input = selector_input.strip()

    if selector_input.startswith('.') or selector_input.startswith('#'):
        return selector_input  # Already a valid CSS selector

    # Handle multiple class names like "col-6 col-md-3 custom-margin"
    if ' ' in selector_input:
        class_parts = selector_input.split()
        return '.' + '.'.join(class_parts)

    # Try ID, class, or tag
    return f"#{selector_input}, .{selector_input}, {selector_input}"


if __name__ == "__main__":
    conn = connect_to_db()
    url = input("Enter the website URL: ").strip()
    
    block_selector_input = input("Enter the block selector (tag/class/id): ").strip()
    block_selector = normalize_selector(block_selector_input)

    extract_multiple_contacts(url, conn, block_selector)
    conn.close()
