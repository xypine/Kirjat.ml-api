from flask import Flask
from flask_cors import CORS
from flask import jsonify
from flask import request

import scraper
from scraper import scrape


app = Flask(__name__)
app_status_possible = ["OK", "MAINTAIN", "ERR", "OFFLINE"]
app_status = app_status_possible[0]
CORS(app)

c = 0

def booklistTodictList(books):
    out = []
    for i in books:
        out.append(i.to_dict())
    return out
@app.route("/")
def helloWorld():
    view = "<title>A+</title>"
    global c
    c = c + 1
    view = view + "<h2> Kirjat.ml </h2>"
    view = view + "<hr \>"
    view = view + "<form action=\" " + "/query" + "\" method=\"post\">"
    view = view + "<input type=\"text\" name=\"query\">"
    view = view + "<input type=\"submit\">"
    view = view + "</form>"
    view = view + "<br \\><hr \\>"
    view = view + "Kirjat.ml v. " + str(scraper.app_version) + " | <a href=\"https://raw.githubusercontent.com/jonnelafin/A-/master/LICENSE\">LICENSE</a>"
    view += "<p>App status: " + str(app_status) + "</p>"
    return view
@app.route("/query", methods=['POST'])
def query():
    print(request.form)
    if 'query' in request.form.keys():
        books = scrape(request.form.get('query'))
        return jsonify( booklistTodictList(books) )
    return "400: Query form must contain the key \"query\"", 400
if __name__ == "__main__":
    app.run()