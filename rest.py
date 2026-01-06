from flask import Flask, jsonify, request
import json

app = Flask(__name__)

books = [
    {"id": 1, "title": "The Hobbit", "author": "J.R.R. Tolkien"},
    {"id": 2, "title": "1984", "author": "George Orwell"}
]

@app.route("/")
def home():
    return "<h1>HELLO WORLD</h1>"

@app.route('/books', methods=['GET'])
def get_books():
    return json.dumps(books)


@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = next((b for b in books if b['id'] == book_id), None)
    return json.dumps(book) if book else ("Book not found", 404)


@app.route('/books', methods=['POST'])
def add_book():
    new_book = request.get_json()
    books.append(new_book)
    return json.dumps(new_book), 200

if __name__ == '__main__':
    app.run(debug=True)