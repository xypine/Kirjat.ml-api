# -*- coding: utf-8 -*-
# !/usr/bin/env python3
# Script written by Elias Eskelinen aka Jonnelafin
# This script has been licenced under the MIT-License

# import the libraries
from bs4 import BeautifulSoup as soup
from urllib.parse import urlencode, quote_plus
import requests
import os, time, sys

# Base64 for images
import base64

# json for sanomapro
import json

# import internal libraries
from kirja import *

# App meta
app_name = "kirjat.ml"
app_version = "1.0"
app_start_wait = 0

# Store variables
store_url_jam = "https://kauppa.jamera.net"
store_url_search_jam = "https://kauppa.jamera.net/kauppa/haku/?q="
store_url_san = "https://www.sanomapro.fi/"
store_url_search_san = "https://www.sanomapro.fi/haku/?q="
store_url_api_san = "https://api.addsearch.com/v1/search/"

store_domains = [store_url_jam, store_url_san]
store_lang = "fi-FI"
store_lang_short = "fi"


# Is the file already present?
def is_file_already_present(file):
    files = os.listdir()
    return file in files


# Clean a string from ääkköset
def clean(str):
    return str.replace(u'ä', "%E4").replace(u'ö', "%F6").replace(u'å', "%E5")


# Getting the html
def request(url):
    clean_url = url
    headers = {
        "Accept-Language": "fi-FI,fi;q=0.8,en-US;q=0.5,en;q=0.3"}  # {"Accept-Language": store_lang + "," + store_lang_short + ";q=0.1"} #fi-FI,fi;q=0.8,en-US;q=0.5,en;q=0.3
    response = requests.get(clean_url, headers=headers)
    page_html = response.text
    page_soup = soup(page_html, 'html.parser')
    return page_soup
def request_img(url):
    response = requests.get(base64.b64decode(url))
    uri = ("data:" +
           response.headers['Content-Type'] + ";" +
           "base64," + str(base64.b64encode(response.content).decode("utf-8")))
    return uri
def get_products_jam(page_soup, verbose=False):
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
        link = ""
        if len(product_images) > 0:
            img = product_images[0]
            img_href = store_url_jam + "/" + img['src']
            try:
                link = store_url_jam + img.parent['href']
            except Exception as e:
                print("Couldn't get the link: " + e)
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
        tuotteet.append(kirja(name, price, prices, conditions, id, img_href, link))
    return tuotteet

price_cache = {}
def get_price_san(url):
    global price_cache
    if url in price_cache.keys():
        return price_cache[url]
    soup = request(url)
    prices = soup.find_all('span', {'class': 'price'})
    cond = soup.find_all('span', {'class': 'product-name'})
    out = []
    conditions = []
    for i in prices:
        out.append(i.text.replace(",", "").replace("€", "").replace(" ","").replace("\xa0", "").replace(u'\xa0', ""))
    for i in cond:
        conditions.append(i.text)
    if out == []:
        saveHTML(str(soup))
    price_cache[url] = [out, conditions]
    return out, conditions
def get_products_san(page_soup, verbose=False, keyword=""):
    tuotteet = []
    key = str(page_soup).split("?key=")[1].split("&")[0]
    print("key: " + key)
    url = store_url_api_san + key + "?term=" + keyword + "&fuzzy=auto&page=1&limit=20&sort=relevance&order=desc"
    print("Making a request to " + url)
    soup = request(url)
    data = json.loads(str(soup))
#    print("Data:")
#    print(data)
    books = data["hits"]
    for i in books:
        iurl = i["url"]
        prices, conditions = get_price_san(iurl)
        price = int(i["score"])
        if len(prices) > 0:
            price = int(prices[len(prices)-1])
        tuotteet.append(kirja(i["title"], price, prices, conditions, i["id"], i["images"]["main"], iurl))
    return tuotteet

kirjat_scrape_err = ""


def scrape_jam(bookname="Tekijä Pitkä matematiikka 3"):
    global store_url_jam, store_url_search_jam, kirjat_scrape_err
    print("Getting the HTML...")
    book = bookname
    book = clean(book)
    soup = request(store_url_search_jam + book)
    print("Getting the HTML...OK")
    print("Parsing the HTML for products...")
    products = get_products_jam(soup, True)
    if products == []:
        err = parse_error(soup)
        if err == "":
            print("Apparently no products were found, here is the HTML for debugging:")
            print(soup)
        else:
            print("Store returned this error: ")
            kirjat_scrape_err = err
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
    print("Best match price: " + best.my_price_to_e())
    print("Parsing the HTML for products...OK")
    return products

def saveHTML(html):
    with open("debug.html", "w+") as f:
        f.write(html)
        f.close()
def scrape_san(bookname="Tekijä Pitkä matematiikka 3"):
    global store_url_san, store_url_search_san, kirjat_scrape_err
    print("Getting the HTML...")
    book = bookname
    book = clean(book)
    print("Url: " + str(store_url_search_san)) # + book
    soup = request(store_url_search_san + book)
    print("Getting the HTML...OK")
    print("Parsing the HTML for products...")
    products = get_products_san(soup, True, bookname)
    #return []
    if products == []:
        err = parse_error(soup)
        if err == "":
            print("Apparently no products were found, saving the HTML for debugging...")
            saveHTML(str(soup))
            print("HTML saved to debug.html")
        else:
            print("Store returned this error: ")
            kirjat_scrape_err = err
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
    print("Best match price: " + best.my_price_to_e())
    print("Parsing the HTML for products...OK")
    return products

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
        bookname = clean(bookname)
        #        bookname = urlencode(bookname, quote_via=quote_plus)
        #        print("Encoding " + str(bookname) + "...")
        #        bookname = bookname.encode('windows-1250')
        #        bookname = bookname.decode('latin-1')
        soup = request(store_url_search_jam + str(bookname))
        print("Scraping " + str(store_url_search_jam + str(bookname)))
        products = get_products_jam(soup, True)
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
    print("-----------------------")
    print(kirja().price_to_e(total) + "e in total. ")
    print("( " + str(total) + " )")
    print("-----------------------")
    return result


def banner():
    print("    __ __  _        _         __                 __")
    print("   / //_/ (_)_____ (_)____ _ / /_    ____ ___   / /")
    print("  / ,<   / // ___// // __ `// __/   / __ `__ \ / / ")
    print(" / /| | / // /   / // /_/ // /_ _  / / / / / // /  ")
    print("/_/ |_|/_//_/ __/ / \__,_/ \__/(_)/_/ /_/ /_//_/  ")
    print("             /___/                                ")


if __name__ == "__main__":
    banner()
    print(app_name + " scraper version " + app_version)
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
        print("Query mode: sanomapro")
        scrape_san(input("Query: "))

    print("Scrape finished")
