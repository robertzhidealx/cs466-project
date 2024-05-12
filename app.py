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

  docs = process_query(title, query, author, stem, removestop, weighting, similarity, weights, count)

  return jsonify(docs)

@app.route("/doc", methods=["GET"])
def doc():
  id = request.args.get("id")

  docs = get_doc(int(id))

  return jsonify(docs)
