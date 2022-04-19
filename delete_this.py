from scraper.models import connect_db, check_version, close_conn, create_tables, add_job_type1, add_job_type2, add_state, add_company_detail, add_job
from scraper.extractor import extract_categories
from scraper.webdriver import create_driver

def main():
    conn = connect_db()
    
    import json
    with open("companies_Data.txt") as f:
        companies = json.load(f)
    
    for company in companies:
        name = company.get("Company name")
        desc = company.get("Description")
        state = company.get("Location")
        subcategory = company.get("State")

        print(name, desc, state, subcategory)
        add_company_detail(conn, name, desc, state, subcategory)




if __name__ == "__main__":
    # main()
    driver = create_driver()
    extract_categories(driver)
    driver.close()