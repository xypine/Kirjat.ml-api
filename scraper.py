# -*- coding: utf-8 -*-
# !/usr/bin/env python3
# Script written by Elias Eskelinen aka Jonnelafin
# This script has been licenced under the MIT-License

# import the libraries
from bs4 import BeautifulSoup as soup
from urllib.parse import urlencode, quote_plus
import requests
import os, time, sys

# import internal libraries
from kirja import *

# App meta
app_name = "kirjat.ml scraper"
app_version = "1.0"
app_start_wait = 0

# Store variables
store_url = "https://kauppa.jamera.net"
store_url_search = "https://kauppa.jamera.net/kauppa/haku/?q="
store_lang = "fi-FI"
store_lang_short = "fi"


# Is the file already present?
def is_file_already_present(file):
    files = os.listdir()
    return file in files


# Getting the html                                        
def request(url):
    clean_url = url
    headers = {
        "Accept-Language": "fi-FI,fi;q=0.8,en-US;q=0.5,en;q=0.3"}  # {"Accept-Language": store_lang + "," + store_lang_short + ";q=0.1"} #fi-FI,fi;q=0.8,en-US;q=0.5,en;q=0.3
    response = requests.get(clean_url, headers=headers)
    page_html = response.text
    page_soup = soup(page_html, 'html.parser')
    return page_soup


def get_products(page_soup, verbose=False):
    if len(page_soup.find_all('table', {'class': 'tuotteet_flex'})) < 1:
        print("Failed to find the product container from the provided HTML, returning an empty array.")
        return []
    table = page_soup.find_all('table', {'class': 'tuotteet_flex'})[0]
    containers = table.findAll("tr", recursive=False)
    if verbose:
        print("Found " + str(len(containers)) + " product containers.")
    tuotteet = []
    for container in containers:
        product_images = container.find_all('img', {'class': 'tuote_kuva'}, recursive=True)
        product_name = container.find_all('a', {'class': 'otsikko'}, recursive=True)
        product_possible_price = container.find_all('td', {'class': 'radio'})

        img_href = ""
        if len(product_images) > 0:
            img = product_images[0]
            img_href = store_url + "/" + img['src']
        price = -1
        prices = []
        condition = ""
        conditions = []
        id = 0
        for radio in product_possible_price:
            product_price = radio.find_all('label')
            if len(product_price) > 0:
                price_sub = product_price[0]
                condition_possible = price_sub.find_all('p', {'class': 'name'})
                if len(condition_possible) > 0:
                    c = condition_possible[0].text
                    condition = c
                    conditions.append(c)
                price_possible = price_sub.find_all('span')
                if len(price_possible) > 0:
                    try:
                        p = int(price_possible[0].text.replace("€", "").replace(",", ""))
                        price = p  # 13,30 € -> 1330
                        prices.append(p)
                    except Exception as e:
                        price = -2
        name = ""
        if len(product_name) > 0:
            name = product_name[0].text
            ids = product_name[0].parent.findAll("a")
            if len(ids) > 1:
                id = ids[0]["name"]
        tuotteet.append(kirja(name, price, prices, conditions, id, img_href))
    return tuotteet


def scrape(bookname="Tekijä Pitkä matematiikka 3"):
    global store_url, store_url_search
    print("Getting the HTML...")
    book = bookname
    book = book.replace(u'ä', "%E4")
    book = book.replace(u'ö', "%F6")
    soup = request(store_url_search + book)
    print("Getting the HTML...OK")
    print("Parsing the HTML for products...")
    products = get_products(soup, True)
    if products == []:
        err = parse_error(soup)
        if err == "":
            print("Apparently no products were found, here is the HTML for debugging:")
            print(soup)
        else:
            print("Store returned this error: ")
            print(err)
    ind = 0
    best = kirja()
    bestDiff = 99999999
    ind = 0
    for i in products:
        diff = set(i.name).difference(set(bookname))
        dif = len(diff) + ind * 4
        print(str(i) + " | " + str(dif))

        if i.price > -1:
            diff = set(i.name).difference(set(bookname))
            diff2 = abs(len(bookname) - len(i.name))
            dif = len(diff) + ind * 4
            if dif < bestDiff:
                bestDiff = dif
                best = i
                print(dif)
        ind += 1
    print("\n\nBest match: " + str(best))
    print("Best match image: " + best.image)
    print("Parsing the HTML for products...OK")


def parse_error(soup):
    errors = soup.find_all('div', {'class': 'error'})
    if len(errors) < 1:
        return ""
    return errors[0].text


def scrape_from_file(filename):
    result = []
    lines = ""
    with open(filename, "r", encoding="utf-8") as f:
        lines = f.readlines()
    total = 0
    for i in lines:
        bookname = i.replace("\n", "")
        booknameo = i.replace("\n", "")
        bookname = bookname.replace(u'ä', "%E4")
        bookname = bookname.replace(u'ö', "%F6")
        #        bookname = urlencode(bookname, quote_via=quote_plus)
        #        print("Encoding " + str(bookname) + "...")
        #        bookname = bookname.encode('windows-1250')
        #        bookname = bookname.decode('latin-1')
        soup = request(store_url_search + str(bookname))
        print("Scraping " + str(store_url_search + str(bookname)))
        products = get_products(soup, True)
        bestDiff = 99999
        best = kirja()
        ind = 0
        for b in products:
            if b.price > -1:
                diff = set(b.name).difference(set(booknameo))
                diff2 = abs(len(booknameo) - len(b.name))
                dif = len(diff) + ind * 4
                if dif < bestDiff:
                    bestDiff = dif
                    best = b
                    print(dif)
            #                result.append(b)
            #                break
            ind += 1
        result.append(best)
        total += best.price
    print(str(total) + " in total.")
    return result


if __name__ == "__main__":
    print("    __ __  _        _         __                 __")
    print("   / //_/ (_)_____ (_)____ _ / /_    ____ ___   / /")
    print("  / ,<   / // ___// // __ `// __/   / __ `__ \ / / ")
    print(" / /| | / // /   / // /_/ // /_ _  / / / / / // /  ")
    print("/_/ |_|/_//_/ __/ / \__,_/ \__/(_)/_/ /_/ /_//_/  ")
    print("             /___/                                ")
    print(app_name + " version " + app_version)
    print("Licensed under the MIT-License by Elias Eskelinen 2020")
    print("Starting scraping in " + str(
        app_start_wait) + " seconds, please be adviced: this could be illegal in your region and time.")
    print("Press Ctrl+C to cancel at any time.")
    time.sleep(app_start_wait)

    if len(sys.argv) > 1:
        file = sys.argv[1]
        print("Detected file as input, checking if it exists...")
        print(str(file))
        was = is_file_already_present(file)
        if was:
            scrap = scrape_from_file(file)
            for i in scrap:
                print(i)
        else:
            print("File not found.")
    else:
        scrape(input("Query: "))

    print("Scrape finished")
