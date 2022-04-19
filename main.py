from scraper.utils import Cache, to_file, traceback
from scraper.extractor import load_categories
from scraper.webdriver import linkedin_login, get_jobs_by_location, create_driver, scrape_companies
from scraper.models import connect_db, close_conn, create_tables, add_job_type1, add_job_type2, add_state, add_company_detail, add_job



def main(driver, login_required= True):

    load_categories(driver)

    if login_required:
        linkedin_login(driver)
    
    get_jobs_by_location(driver, locations= ["Jharkhand", "Bihar", "Kolkata", "Bengaluru", "Tamil Nadu"])

    print('\n\nData has been scraped...')
    print("Storing the data in file(s)")

    to_file("Data_Copy.txt", values= Cache.data)

    Cache.save("Data")

    print("Scraping the companies...")
    scrape_companies(driver)
    Cache.save_companies("Data")

    print("Companies have been scraped.")



# Current structure:   main() -> get_jobs_by_location() -> get_jobs() -> scrape_jobs() -> scrape_companies

if __name__ == "__main__" :

    driver = create_driver()
    try:
        main(driver)

    except Exception as e:
        print(e, type(e))
        print(traceback.format_exc())

    finally:
        driver.quit()
        to_file("Remaining_data.txt", values= Cache.data)
        