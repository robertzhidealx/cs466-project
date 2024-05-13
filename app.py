from flask import Flask, request, jsonify
from flask_cors import CORS
from query import process_query, get_doc

app = Flask(__name__)
cors = CORS(app)

@app.route("/")
def home():
  return "Welcome to Doc Search Engine!"

@app.route("/search", methods=["GET"])
def search():
  title = request.args.get("title")
  query = request.args.get("query")
  author = request.args.get("author")
  stem = True if request.args.get("stem") == "true" else False
  removestop = True if request.args.get("remove") == "true" else False
  weighting = request.args.get("weighting")
  similarity = request.args.get("similarity")
  weights = request.args.get("weights")
  count = request.args.get("count")
  count = -1 if count == "" else int(count)
  domain = request.args.get("domain")
  online = True if request.args.get("online") == "true" else False
  numPages = 100
  numPages = request.args.get("numPages")
  numPages = -1 if numPages == "" else int(numPages)

  docs = process_query(title, query, author, stem, removestop, weighting, similarity, weights, count, domain, online, numPages)

  return jsonify(docs)
