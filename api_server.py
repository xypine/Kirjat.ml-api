# -*- coding: utf-8 -*-
# !/usr/bin/env python3
# Script written by Elias Eskelinen aka Jonnelafin
# This script has been licenced under the MIT-License

import os
from flask import Flask
from flask_cors import CORS
from flask import jsonify
from flask import request

import base64

import scraper
from scraper import scrape, banner


app = Flask(__name__)
app_status_possible = ["OK", "MAINTAIN", "ERR", "OFFLINE"]
app_status = app_status_possible[0]
CORS(app)

c = 0

cache = {}

flag_nocache = False

def booklistTodictList(books):
    out = []
    for i in books:
        out.append(i.to_dict())
    return out
@app.route("/")
def helloWorld():
    view = "<title>Kirjat.ml</title>"
    global c
    c = c + 1
    view = view + "<h2> Kirjat.ml api </h2>"
    view = view + "<hr \>"
    view = view + "<form action=\" " + "/api/v1" + "\" method=\"post\">"
    view = view + "<input type=\"text\" name=\"query\">"
    view = view + "<input type=\"submit\">"
    view = view + "</form>"
    view += "<a href=\"/batch\"> Try batch query instead </a>"
    view = view + "<br \\><hr \\>"
    view = view + "Kirjat.ml api v. " + str(scraper.app_version) + " | <a href=\"https://raw.githubusercontent.com/jonnelafin/A-/master/LICENSE\">LICENSE</a>"
    view += "<p>App status: " + str(app_status) + "</p>"
    view += str(c) + " Requests since last boot"
    return view
@app.route("/batch")
def batch():
    view = "<title>Kirjat.ml batch query</title>"
    global c
    c = c + 1
    view = view + "<h2> Kirjat.ml api batch query</h2>"
    view = view + "<hr \>"
    view = view + "<form action=\" " + "/api/v1" + "\" method=\"post\">"
    view = view + "<textarea name=\"querym\" rows=\"10\" cols=\"80\"> Type your books here, each on it's own line </textarea>"
    view += "<br><br>"
    view = view + "<input type=\"submit\">"
    view = view + "</form>"
    view += "<a href=\"/\"> Back </a>"
    view = view + "<br \\><hr \\>"
    view = view + "Kirjat.ml api v. " + str(scraper.app_version) + " | <a href=\"https://raw.githubusercontent.com/jonnelafin/A-/master/LICENSE\">LICENSE</a>"
    view += "<p>App status: " + str(app_status) + "</p>"
    view += str(c) + " Requests since last boot"
    return view
@app.route("/api/v1", methods=['POST'])
def query():
    print(request.form)
    if 'query' in request.form.keys():
        bookname = request.form.get('query')
        usedCache = False
        if not bookname in cache.keys() or flag_nocache:
            print("\"" + bookname + "\" not in cache, scraping...")
            books = scrape(bookname)
            err = scraper.clean(scraper.kirjat_scrape_err)
            cache[bookname] = (books, err)
        else:
            usedCache = True
            print("\"" + bookname + "\" in cache.")
            books, err = cache[bookname]
        return jsonify({"data": booklistTodictList(books), "cached_result": usedCache, "err": err, "query": bookname})
    if 'querym' in request.form.keys():
        booknames = request.form.get('querym').split("\n")
        print("Queries: " + str(booknames))
        result = []
        query = []
        for book in booknames:
            bookname = book.replace("\r", "").replace("\n", "")
            query.append(bookname)
            usedCache = False
            if not bookname in cache.keys() or flag_nocache:
                print("\"" + bookname + "\" not in cache, scraping...")
                books = scrape(bookname)
                err = scraper.clean(scraper.kirjat_scrape_err)
                cache[bookname] = (books, err)
            else:
                usedCache = True
                print("\"" + bookname + "\" in cache.")
                books, err = cache[bookname]
            result.append({"data": booklistTodictList(books), "cached_result": usedCache, "err": err, "query": query})
        return jsonify(result)
    return jsonify({"code": 400, "reason": "400: Query form must contain the key \"query\" or \"querym\"", "stacktrace": ""}), 400
@app.route("/api/v1_img|<url>")
def img(url):
    try:
        if not "kauppa.jamera.net" in str(base64.b64decode(bytes(url, 'utf-8'))):
            return jsonify({"code": 403, "reason": "invalid url domain", "stacktrace": ""}), 404
        try:
            uri = scraper.request_img(url)
            return str(uri)
        except Exception as e:
            return jsonify({"code" : 404, "reason": "malformed url", "stacktrace": str(e)}), 404
    except Exception as e:
        return jsonify({"code" : 500, "reason": "?", "stacktrace": str(e)}), 500
if __name__ == '__main__':
    banner()
    print(scraper.app_name + " api version " + scraper.app_version)
    print("Licensed under the MIT-License by Elias Eskelinen 2020")
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
