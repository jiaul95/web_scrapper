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


def categorize_tags(tags):
    company_tags, phone_tags, email_tags = [], [], []

    for tag in tags:
        tag_lower = tag.lower()

        if any(kw in tag_lower for kw in ['company', 'comp']) or any(tag_lower.startswith(h) for h in ['h1', 'h2', 'h3']):
            company_tags.append(tag)
        elif 'tel' in tag_lower or 'phone' in tag_lower or "href^='tel" in tag_lower:
            phone_tags.append(tag)
        elif 'email' in tag_lower or 'mailto' in tag_lower or "href^='mailto" in tag_lower:
            email_tags.append(tag)

    if not company_tags:
        company_tags.append("h3.moHeading")
    if not phone_tags:
        phone_tags.append("a[href^='tel']")
    if not email_tags:
        email_tags.append("a[href^='mailto']")

    return company_tags, phone_tags, email_tags


def extract_value(block, selectors, attr='text'):
    for selector in selectors:
        try:
            locator = block.locator(selector)
            count = locator.count()
            if count > 0:
                for i in range(count):
                    el = locator.nth(i)
                    href = el.get_attribute('href') if attr == 'href' else None

                    # If we want phone numbers: ensure href is tel:
                    if attr == 'phone':
                        if href and href.startswith('tel:'):
                            return el.inner_text().strip()
                    elif attr == 'email':
                        if href and href.startswith('mailto:'):
                            return el.inner_text().strip()
                    elif attr == 'href':
                        return href.strip()
                    else:
                        return el.inner_text().strip()
        except:
            continue
    return None



def extract_multiple_contacts(url, tags, conn):
    from playwright.sync_api import sync_playwright
    import time

    company_tags, phone_tags, email_tags = categorize_tags(tags)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print(f"Opening URL: {url}")
        page.goto(url)
        page.wait_for_load_state("domcontentloaded")
        time.sleep(3)

        # Try clicking "View More" if it exists
        try:
            while True:
                view_more_button = page.locator("div.more-cat-link p:has-text('View More')")
                if view_more_button and view_more_button.is_visible():
                    print("Clicking 'View More' button...")
                    view_more_button.click()
                    time.sleep(2)
                else:
                    print("'View More' button not found or not visible.")
                    break
        except Exception as e:
            print(f"No 'View More' found or error occurred: {e}. Proceeding with available content.")

        # Try locating company blocks
        company_blocks = page.locator("div.col-6.col-md-3.custom-margin")
        count = company_blocks.count()

        if count == 0:
            print("No company blocks found. Extracting single contact from the page.")

            block = page  # Use the full page as a block

            company_name = extract_value(block, company_tags)
            phone = extract_value(block, phone_tags, attr='href')
            if phone and phone.startswith("tel:"):
                phone = phone.replace("tel:", "").strip()

            email = extract_value(block, email_tags, attr='href')
            if email and email.startswith("mailto:"):
                email = email.replace("mailto:", "").strip()

            print(f"Company: {company_name}, Phone: {phone}, Email: {email}")

            if company_name and phone:
                save_to_db(conn, company_name, email, phone)
            else:
                print("Skipping entry: Missing company name or phone.")
        else:
            print(f"Total company blocks found: {count}")

            for i in range(count):
                block = company_blocks.nth(i)

                company_name = extract_value(block, company_tags)
                phone = extract_value(block, phone_tags, attr='href')
                if phone and phone.startswith("tel:"):
                    phone = phone.replace("tel:", "").strip()

                email = extract_value(block, email_tags, attr='href')
                if email and email.startswith("mailto:"):
                    email = email.replace("mailto:", "").strip()

                print(f"{i+1}. Company: {company_name}, Phone: {phone}, Email: {email}")

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
