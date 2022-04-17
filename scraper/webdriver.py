from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from .extractor import load_categories
from .utils import Cache, os, re, time, urlify, By


# To get find an element inside the driver page and wait until it is loaded fully
def get_element(driver, by, value):
    try:
        element = WebDriverWait(driver, Cache.sleep_time).until(EC.presence_of_element_located((by, value)))
        return element
    except TimeoutException:
        print("Too much time taken for loading that element, please increase the delay.")



# To load all requested elements inside the driver page and wait until all are loaded properly
def get_elements(driver, by, value):
    try:
        element_list = WebDriverWait(driver, Cache.sleep_time).until(EC.presence_of_all_elements_located((by, value)))
        return element_list
    except TimeoutException:
        print("Too much time taken for loading that element, please increase the delay.")



# Creates a new driver and returns it
def create_driver():
    """
    Returns a new driver after each time it is called
    """
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()

    return driver


   

# For logging into the LinkedIn account using the details given in the '.env' file 
def linkedin_login(driver):
    """
    For logging in, the '.env' file should look like this:
    export email="<your login email>"
    export password="<your login password>"
    """
    driver.get('https://linkedin.com/')

    time.sleep(3) # Let the user actually see something!

    email_input = driver.find_element(By.XPATH, '//input[@id="session_key" and @class="input__input"]')
    email_input.send_keys(os.environ.get('email'))

    password_input = driver.find_element(By.XPATH, '//input[@id="session_password" and @class="input__input"]')
    password_input.send_keys(os.environ.get('password'))

    password_input.submit()

    return None



# For giving time to the website to load all the contents
def load_all_contents_by_scrolling(driver, sec= 1):
    start = time.time()
    
    # will be used in the while loop
    initialScroll = 0
    finalScroll = 1000
    
    while True:
        driver.execute_script(f"window.scrollTo({initialScroll}, {finalScroll})")
        # this command scrolls the window starting from
        # the pixel value stored in the initialScroll 
        # variable to the pixel value stored at the
        # finalScroll variable
        initialScroll = finalScroll
        finalScroll += 1000
    
        # we will stop the script for 3 seconds so that 
        # the data can load
        time.sleep(1)
        # You can change it as per your needs and internet speed
    
        end = time.time()
    
        # We will scroll for "sec" seconds.
        # You can change it as per your needs and internet speed
        if round(end - start) > sec:
            break



# This function scrapes the website when the driver is loaded onto a specific page
def scrape_jobs(driver):
    """
    When the driver is on the job results page, this function scrapes the webpage for finding the the jobs
    """
    print("\nNow scraping the data\n")

    # import pdb; pdb.set_trace()                       # For debugging purposes
    # to_file("search.html", driver.page_source)

    page_text = driver.page_source

    # When there are spelling errors, reload the page with the link given in the spell correction
    if re.search("Did you mean", page_text, re.I):
        print("Spelling Error...")
        dym = get_element(driver, By.XPATH, '//a[contains(@data-trk-control-name, "spell_correction_suggestion")]')
        driver.get(str(dym.get_attribute('href')))
        print("Refreshing...")
        scrape_jobs(driver)
        return

    # When there are no jobs available for that category and location, skip the extraction
    if re.search("No matching jobs found.", page_text, re.I):
        print("No jobs available for this category at this state")
        return
    
    # When the page isn't loading, it is broken, hence skipping the page
    if re.search(r"Unfortunately, things aren’t loading", page_text, re.I):
        print("This page is broken, skipping data extraction process...")
        return

    # Load the entire page for 5 seconds
    load_all_contents_by_scrolling(driver, 5)

    jobs = get_elements(driver, By.XPATH, '//li[contains(@class, "jobs-search-results__list-item")]')
    i = 0

    for job in jobs:
        
        try:
            job_info = job.text.splitlines()
            company = get_element(job, By.XPATH, '//a[contains(@data-control-name, "job_card_company_link")]')

            job_title, job_company, job_location, job_type, *_ = job_info
            res = f'{job_title} by {job_company} at {job_location}' + str(f'({job_type})' if job_type else ' ')
            Cache.store(res, company.get_attribute("href"))
            
            i += 1

        except ValueError:
            continue

    
    print("Jobs scraped:", i)

    return



# For getting to the search results page with each given category, if no location given, defaults to India
def get_jobs(driver, location= "India"):
    """
    Loads from the categories given inside the cache, if not present, calls the extractor to load it.
    When KeyboardInterrupt signal is found, stops the data extraction, and saves all the collected into the file.
    """
    if not Cache.categories:
        categories = load_categories(driver)
    else:
        categories = Cache.categories

    print("Getting jobs for location:", location)
    try:   
        for categ in categories:
            if not categ: continue          # Skip lines that are empty
            print("\nStarting scraping for category:", categ, "And location:", location, "\n")

            driver.get(f"https://linkedin.com/jobs/search/?location={urlify(location)}&keywords={urlify(categ)}")

            scrape_jobs(driver)
    
    except KeyboardInterrupt:
        Cache.save(filename= "Data", access_type= "a")
        
 

 # When jobs are to be searched in specific states, this function is called
def get_jobs_by_location(driver, locations= []):
    """
    Calls the get_jobs() function repeated by each call having different location.
    Also when no location is given, defaults to India.
    """
    if not locations:
        locations = []
        locations.append("India")        # If no location given, searches with Country location
    
    for loc in locations:
        get_jobs(driver, loc)
    
    Cache.save("Data")
        
    return



# To scrape companies with links given inside a file
def scrape_companies(driver, file= "all_companies.txt"):
    if not Cache.companies:
        with open(file) as f:
            Cache.companies = f.readlines()
    
    companies = set(Cache.companies)

    for comp in companies:
        try:
            driver.get(comp)
            comp_info = get_element(driver, By.XPATH, '//div[contains(@class, "org-top-card__primary-content")]')
            comp_desc = get_element(driver, By.XPATH, '//p[contains(@class, "break-words white-space-pre-wrap mb5 text-body-small t-black--light")]')
            m = re.finditer("\d+", comp_info.text)
            m = list(m)
            comp_name, comp_location = comp_info.text[:m[0].start()].splitlines()
            comp_emps = ','.join([a.group() for a in m])[:-1]

            content = {
                "Company name" : comp_name,
                "Description" : comp_desc,
                "Location" : comp_location,
                "Employees" : comp_emps,
            }

            Cache.store_company(content)
        except (ValueError or TimeoutError or TimeoutException):
            continue