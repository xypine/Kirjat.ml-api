# Script written by Elias Eskelinen aka Jonnelafin

# import the libraries
from bs4 import BeautifulSoup as soup
import requests
import os, time

# import internal libraries
from kirja import *

# App meta
app_name = "hinnat.ml api"
app_version = "1.0"
app_start_wait = 0

# Store variables
store_url = "https://kauppa.jamera.net"
store_url_search = "https://kauppa.jamera.net/kauppa/haku/?q="


# Is the file already present?
def is_file_already_present(file):
    files = os.listdir()
    return file in files


# Getting the html                                        
def request(url):
    response = requests.get(url)
    page_html = response.text
    page_soup = soup(page_html, 'html.parser')
    return page_soup


def get_products(page_soup, verbose=False):
    table = page_soup.find_all('table', {'class': 'tuotteet_flex'})[0]
    containers = table.findAll("tr", recursive=False)
    if verbose:
        print("Found " + str(len(containers)) + " product containers.")
    tuotteet = []
    for container in containers:
        product_images = container.find_all('table', {'class': 'kuva'})
        product_name = container.find_all('a', {'class': 'otsikko'}, recursive=True)
        tuotteet.append(kirja("Yeet", 99, "kuva"))
    return tuotteet

def scrape():
    global store_url, store_url_search
    print("Getting the HTML...")
    soup = request(store_url_search + "Nos vemos! 3")
    print("Getting the HTML...OK")
    print("Parsing the HTML for products...")
    print( get_products(soup) )
    print("Parsing the HTML for products...OK")

if __name__ == "__main__":
    print("  _    _ _                   _               _ ")
    print(" | |  | (_)                 | |             | |")
    print(" | |__| |_ _ __  _ __   __ _| |_   _ __ ___ | |")
    print(" |  __  | | '_ \| '_ \ / _` | __| | '_ ` _ \| |")
    print(" | |  | | | | | | | | | (_| | |_ _| | | | | | |")
    print(" |_|  |_|_|_| |_|_| |_|\__,_|\__(_)_| |_| |_|_|")
    print("-----------------------------------------------")
    print(app_name + " version " + app_version)
    print("Licensed under the MIT-License by Elias Eskelinen 2020")
    print("Starting scraping in " + str(
        app_start_wait) + " seconds, please be adviced: this could be illegal in your region and time.")
    print("Press Ctrl+C to cancel at any time.")
    time.sleep(app_start_wait)

    scrape()

    print("Scrape finished")
