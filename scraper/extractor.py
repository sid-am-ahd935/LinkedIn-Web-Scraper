from .utils import to_file, time, os, By



# To extract all the job categories available by the generic website
## Note this scrapper function only works with this website.
def extract_categories(driver, to_exclude= [], name= "all_categories.txt"):
    driver.get('https://careerguide.com/career-options')
    time.sleep(3)                                                       # Giving browser time to load all things
    categories = dict()
    to_exclude = set(to_exclude)

    # This website is in the form of a matrix of divs:
    ## div[1]:  1   2   3
    ## div[2]:  1   2   3
    ## div[3]:  1   2   3
    ## .
    ## .
    ## .
    ## div[13]: 1   2   3

    for i in range(1, 13 + 1):
        for j in range(1, 3 + 1):
            column_element = driver.find_element(By.XPATH, f'//*[@id="aspnetForm"]/div[6]/div[2]/div/div[2]/div/div[{i}]/div[{j}]')
            element_text = column_element.text.split("\n")
            category = element_text[0]

            if category in to_exclude:
                continue

            sub_category = element_text[1:]
            categories[category] = sub_category

    # JSON file for viewing purposes only
    to_file("categories.json", key_values= categories)

    # Creating a text file for storing all categories in each new line
    categories = sum(categories.values(), [])
    to_file(name, values= categories)
    
    return categories



# To load all the categories from the stored file
def load_categories(driver, path= ".", name= "all_categories.txt"):
    if name not in os.listdir():
        return extract_categories(driver, to_exclude= ["Institutes in India", "Exams and Syllabus"])

    with open(os.path.join(path, name)) as f:
        categories  = f.readlines()
    
    return categories
