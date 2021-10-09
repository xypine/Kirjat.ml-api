# -*- coding: utf-8 -*-
# !/usr/bin/env python3
# Script written by Elias Eskelinen aka Jonnelafin
# This script has been licenced under the MIT-License

import os
from flask import Flask
from flask_cors import CORS
from flask import jsonify
from flask import request
from flask import render_template

import base64

import scraper
from scraper import scrape_jam, banner, scrape_san


app = Flask(__name__)
app_status_possible = ["OK", "MAINTAIN", "ERR", "OFFLINE"]
app_status = app_status_possible[0]
CORS(app)

c = 0

cache = {}
cache_san = {}

flag_nocache = False

def booklistTodictList(books):
    out = []
    for i in books:
        if not (i.image == "" and i.price == -1 and i.name == "" and i.conditions == []): # The book is invalid
            out.append(i.to_dict())
    return out
@app.route("/jamera")
def jam():
    global c
    c = c + 1
    return render_template('index.html', endpoint="/api/v1", c=str(c), app_status=app_status, bookstore="Jamera", name="query", app_version = scraper.app_version, hint="Type the name of the book you want to search here.")

@app.route("/jamera_v2")
def jam_v2():
    global c
    c = c + 1
    return render_template('index.html', endpoint="/api/v2", c=str(c), app_status=app_status, bookstore="Jamera (API V2)", name="queryjamera", app_version = scraper.app_version, hint="Type the name of the book you want to search here.")


@app.route("/batchjamera")
def batch():
    global c
    c = c + 1
    return render_template('index.html', endpoint="/api/v1", c=str(c), app_status=app_status, bookstore="Jamera-monihaku", name="querym", app_version = scraper.app_version, hint="Type your books here, each on it's own line")

@app.route("/sanoma")
def san_v2():
    global c
    c = c + 1
    return render_template('index.html', endpoint="/api/v1", c=str(c), app_status=app_status, bookstore="Sanomapro", name="querysan", app_version = scraper.app_version, hint="Type the name of the book you want to search here.")

@app.route("/sanoma_v2")
def san():
    global c
    c = c + 1
    return render_template('index.html', endpoint="/api/v2", c=str(c), app_status=app_status, bookstore="Sanomapro (API V2)", name="querysanomapro", app_version = scraper.app_version, hint="Type the name of the book you want to search here.")

@app.route("/batchsanoma")
def batchsanoma():
    global c
    c = c + 1
    return render_template('index.html', endpoint="/api/v1", c=str(c), app_status=app_status, bookstore="Sanomapro-monihaku", name="querymsan", app_version = scraper.app_version, hint="Type your books here, each on it's own line")

@app.route("/")
def batchmix():
    global c
    c = c + 1
    return render_template('index.html', endpoint="/api/v2", c=str(c), app_status=app_status, bookstore="Täysi monihaku (API V2)", name="queryall", app_version = scraper.app_version, hint="Type your books here, each on it's own line")

@app.route("/api/v1", methods=['POST'])
def query():
    print(request.form)
    if 'query' in request.form.keys():
        bookname = request.form.get('query')
        usedCache = False
        if not bookname in cache.keys() or flag_nocache:
            print("\"" + bookname + "\" not in cache, scraping...")
            books = scrape_jam(bookname)
            err = scraper.clean(scraper.kirjat_scrape_err)
            cache[bookname] = (books, err)
        else:
            usedCache = True
            print("\"" + bookname + "\" in cache.")
            books, err = cache[bookname]
        scraper.kirjat_scrape_err = ""
        return jsonify({"data": booklistTodictList(books), "cached_result": usedCache, "err": err, "query": bookname})
    if 'querysan' in request.form.keys():
        bookname = request.form.get('querysan')
        usedCache = False
        if not bookname in cache_san.keys() or flag_nocache:
            print("\"" + bookname + "\" not in cache, scraping...")
            books = scrape_san(bookname)
            err = scraper.clean(scraper.kirjat_scrape_err)
            cache_san[bookname] = (books, err)
        else:
            usedCache = True
            print("\"" + bookname + "\" in cache.")
            books, err = cache_san[bookname]
        scraper.kirjat_scrape_err = ""
        return jsonify({"data": booklistTodictList(books), "cached_result": usedCache, "err": err, "query": bookname})
    if 'querym' in request.form.keys():
        booknames = request.form.get('querym').split("\n")
        print("Queries: " + str(booknames))
        result = []
        query = []
        for book in booknames:
            scraper.kirjat_scrape_err = ""
            bookname = book.replace("\r", "").replace("\n", "")
            query.append(bookname)
            usedCache = False
            if not bookname in cache.keys() or flag_nocache:
                print("\"" + bookname + "\" not in cache, scraping...")
                books = scrape_jam(bookname)
                err = scraper.clean(scraper.kirjat_scrape_err)
                cache[bookname] = (books, err)
            else:
                usedCache = True
                print("\"" + bookname + "\" in cache.")
                books, err = cache[bookname]
                scraper.kirjat_scrape_err = ""
            result.append({"data": booklistTodictList(books), "cached_result": usedCache, "err": err, "query": query})
        return jsonify(result)
    if 'querymsan' in request.form.keys():
        booknames = request.form.get('querymsan').split("\n")
        print("Queries: " + str(booknames))
        result = []
        query = []
        for book in booknames:
            scraper.kirjat_scrape_err = ""
            bookname = book.replace("\r", "").replace("\n", "")
            query.append(bookname)
            usedCache = False
            if not bookname in cache_san.keys() or flag_nocache:
                print("\"" + bookname + "\" not in cache, scraping...")
                books = scrape_san(bookname)
                err = scraper.clean(scraper.kirjat_scrape_err)
                cache_san[bookname] = (books, err)
            else:
                usedCache = True
                print("\"" + bookname + "\" in cache.")
                books, err = cache_san[bookname]
                scraper.kirjat_scrape_err = ""
            result.append({"data": booklistTodictList(books), "cached_result": usedCache, "err": err, "query": query})
        return jsonify(result)
    return jsonify({"code": 400, "reason": "400: Query form must contain the key \"query\" or \"querym\"", "stacktrace": ""}), 400


imgCache = {}
@app.route("/api/v1_img|<url>")
def img(url):
    if not url in imgCache.keys() or flag_nocache:
        try:
            if "kauppa.jamera.net" not in str(base64.b64decode(bytes(url, 'utf-8'))):
                res = jsonify({"code": 403, "reason": "invalid url domain", "stacktrace": "with url: " + url}), 404
                imgCache[url] = res
                return res
            try:
                uri = scraper.request_img(url)
                imgCache[url] = uri
                return str(uri)
            except Exception as e:
                res = jsonify({"code" : 404, "reason": "malformed url", "stacktrace": str(e)}), 404
                imgCache[url] = res
                return res
        except Exception as e:
            res = jsonify({"code" : 500, "reason": "?", "stacktrace": str(e)}), 500
            imgCache[url] = res
            return res
    else:
        return imgCache[url]

# Begin V2
def getBooksV2(booknames, store):
    print("[V2] Queries: " + str(booknames))
    result = {}
    for book in booknames:
        scraper.kirjat_scrape_err = ""
        bookname = book.replace("\r", "").replace("\n", "")
        
        cacheToUse = cache
        if store == "san":
            cacheToUse = cache_san
        usedCache = False
        if not bookname in cacheToUse.keys() or flag_nocache:
            print("[V2] \"" + bookname + "\" for the store \"" + store + "\" not in cache, scraping...")
            if store == "jam":
                books = scrape_jam(bookname)
            elif store == "san":
                books = scrape_san(bookname)
            else:
                books = []
                print(f"[V2] Invalid store \"{store}\" specified")
            err = scraper.clean(scraper.kirjat_scrape_err)
            cacheToUse[bookname] = (books, err)
        else:
            usedCache = True
            print("[V2] \"" + bookname + "\" for the store \"" + store + "\" in cache.")
            books, err = cache[bookname]
            scraper.kirjat_scrape_err = ""
        result[book] = ({"books": booklistTodictList(books), "result_was_cached": usedCache, "errors": err})
    return result
@app.route("/api/v2", methods=['POST'])
def query_v2():
    print(request.form)
    if 'queryall' in request.form.keys():
        booknames = request.form.get('queryall').split("\n")
        resultJam = getBooksV2(booknames, "jam")
        resultSan = getBooksV2(booknames, "san")
        #result = resultJam + resultSan
        return jsonify({"code" : 200,"result" : {"jamera" : resultJam, "sanomapro" : resultSan}}), 200
    elif 'queryjamera' in request.form.keys():
            booknames = request.form.get('queryjamera').split("\n")
            resultJam = getBooksV2(booknames, "jam")
            return jsonify({"code" : 200,"result" :  resultJam}), 200
    elif 'querysanomapro' in request.form.keys():
            booknames = request.form.get('querysanomapro').split("\n")
            resultSan = getBooksV2(booknames, "san")
            #result = resultJam + resultSan
            return jsonify({"code" : 200,"result" : resultSan}), 200
    return jsonify({"code": 400, "reason": "400: Query form must contain one of the keys \"queryall\", \"queryjamera\" or \"querysanomapro\"", "stacktrace": ""}), 400
    
@app.route("/license")
def license():
    l = "MIT"
    with open("LICENSE", "r+") as f:
        l = f.readlines()
        f.close()
    return "<br />".join(l)
if __name__ == '__main__':
    banner()
    print(scraper.app_name + " api version " + scraper.app_version)
    print("Licensed under the MIT-License by Elias Eskelinen 2021")
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
