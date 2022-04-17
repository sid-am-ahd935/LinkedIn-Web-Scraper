import urllib
import json
import time
import os
import re

from selenium.webdriver.common.by import By


# To make a string into a url
def urlify(string):
    return urllib.parse.quote(string)


# To store contents of a variable in a file
def to_file(name= "", value= '', values= [], key_values= {}, access_type:["w" or "a"]= "w"):
    if not key_values:
        if values and not value:
            value = '\n'.join(values)

        with open(f"{name}", access_type, encoding= "utf-8") as f:
            f.write(value)
    
    else:
        with open(f"{name}", "w") as f:
            json.dump(key_values, f, indent= 3)
 

# To store the loaded categories in the cache
class Cache:
    categories = []
    companies = []
    sleep_time = 5
    # Increase this time if your internet connection is slow
    # But even if it is fast, do not make this less than 2.
    data = list()
    company_data = list()

    @staticmethod
    def store(res : str, company : str):
        Cache.data.append(res)
        Cache.companies.append(company)
    
    @staticmethod
    def store_company(res : str):
        Cache.company_data.append(res)
    
    @staticmethod
    def save(filename : str, access_type:['w' or 'a']= "w"):
        to_file(f"{filename}.txt", access_type= access_type, values= Cache.data)
        to_file(f"all_companies.txt", access_type= access_type, values= list(set(Cache.companies)))

    def save_companies(filename : str, access_type:['w' or 'a']= "w"):
        with open(f"companies_{filename}.txt", access_type) as f:
            json.dump(Cache.company_data, f, indent= 4)