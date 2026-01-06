from flask import Flask, jsonify, request
import json
import copy

app = Flask(__name__)

# books = [
#     {"id": 1, "title": "The Hobbit", "author": "J.R.R. Tolkien"},
#     {"id": 2, "title": "1984", "author": "George Orwell"}
# ]

DEFAULT_FILE_PATH = "database\\books.json"

def get_books_fromdb(file=DEFAULT_FILE_PATH):
    books = {}
    with open(file, "r") as f:
        my_data = f.read()
        books = json.loads(my_data)
    return books

def update_books_at_db(data, file=DEFAULT_FILE_PATH):
    if(type(data) not in [dict, list]):
        return False, "Data is not a dictionary"
    with open(file, "w") as f:
        f.write(json.dumps(data))
    return True, "Data was written successfully"

@app.route("/")
def home():
    return "<h1>HELLO WORLD</h1>"

@app.route('/books', methods=['GET'])
def get_books():
    return (json.dumps(get_books_fromdb()), 200)


@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    books = get_books_fromdb()
    for b in books:
        if b['id'] == book_id:
            return (json.dumps(b), 200)
    return {"result": "Pass", "message": f"Book not found"}, 404
    # book = next((b for b in books if b['id'] == book_id), None)
    # return json.dumps(book) if book else ("Book not found", 404)

@app.route('/books', methods=['POST'])
def add_book():
    new_book: dict = request.data
    try:
        new_book = json.loads(new_book.decode("utf-8"))
    except json.decoder.JSONDecodeError as e:
        return {"result": "Fail", "message": f"Data passed is not JSON"}, 400
    # print(new_book.decode("utf-8"))
    
    # Checking if data passed has some mandatory fields under it or not
    missing_data = [] 
    # if not new_book.get("id", None):
    #     missing_data.append("id")
    if not new_book.get("title", None):
        missing_data.append("title")
    if not new_book.get("author", None):
        missing_data.append("author")
    if not new_book.get("cost", None):
        missing_data.append("cost")
    if missing_data:
        return {"result": "Fail", "message": f"Mandatory Fields missing: {missing_data}"}, 400
    new_book_duplicate = copy.deepcopy(new_book)
    # if Data passed is successfully passing all checks then it is ready to fit into database
    older_data = get_books_fromdb() 
     # Getting older data
    new_book.update({"id": len(older_data)+1})
    older_data.append(new_book)   # attaching new data to older one
    # print(older_data)
    is_updated, message = update_books_at_db(data=older_data)  # writting new data to file/database
    if is_updated:
        return json.dumps(new_book_duplicate), 200  # returning the data that I got as a sign that all check have passed and you data is successfully passed into file/databse
    else:
        return json.dumps({"result": "Fail", "message": f"Something went Wrong! with error: {message}."}), 500  # returning the data that I got as a sign that all check have passed and you data is successfully passed into file/databse
    # return json.dumps({"Hi": 1}), 200

@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    books = get_books_fromdb()
    new_books = []
    for b in books:
        if b["id"] != book_id:
            new_books.append(b)
    update_books_at_db(new_books)
    if len(books) != len(new_books):
        return json.dumps({"message" : f"Book by id: {book_id} deleted successfully"}), 200
    else:
        return json.dumps({"message": "No book Found"}), 200



if __name__ == '__main__':
    app.run(debug=True)




