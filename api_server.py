from flask import Flask
from flask_cors import CORS
from flask import jsonify

from scraper import scrape

app = Flask(__name__)
CORS(app)

def booklistTodictList(books):
    out = []
    for i in books:
        out.append(i.to_dict())
    return out
@app.route("/")
def helloWorld():
    books = scrape()
    return jsonify( booklistTodictList(books) )

if __name__ == "__main__":
    app.run()