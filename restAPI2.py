from flask import Flask, request
import json
import copy
import random

app = Flask(__name__)

DEFAULT_FILE_PATH = "database\\books.json"

def read_file(file_path):
    """This function read file present in file_path and return the json of that object"""
    data = {}
    with open(file_path, "r") as f:
        data = f.read()
    return json.loads(data)
    
def write_file(file_path, data):
    if type(data) not in [dict, list]:
        return False, "data provided was not JSON"
    with open(file_path, "w") as f:
        f.write(json.dumps(data))
    return True, "Data save successfully"

def authorize(header: dict):
    # extract token
    # print(type(header))
    token_by_user = header.get("Authorization")
    # Check if token was there. If not then return 403
    if not token_by_user:
        return False, ({"result": "Fail", "message": "No Authorization provided"}, 403)

    # if Token is there then check if its is valid
    token_data = read_file(file_path="database\\token.json")
    value_in_token_data = token_data.get('logged_data').get(token_by_user)
    if not value_in_token_data or str(value_in_token_data) in ["False"]:
        return False, ({"result": "Fail", "message": "Please Log in First"}, 401)
    return True, ("", 200)

def generate_random():
    return random.randint(20, 30)

@app.route('/books', methods=['GET'])
def get_books():
    is_authorized, message_to_return = authorize(request.headers)
    if not is_authorized:
        return message_to_return
    

    return (read_file(DEFAULT_FILE_PATH), 200)


@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    is_authorized, message_to_return = authorize(request.headers)
    if not is_authorized:
        return message_to_return
    
    books = read_file(DEFAULT_FILE_PATH)
    for b in books:
        if b['id'] == book_id:
            return (json.dumps(b), 200)
    return {"result": "Pass", "message": f"Book not found"}, 404
    # book = next((b for b in books if b['id'] == book_id), None)
    # return json.dumps(book) if book else ("Book not found", 404)
    
@app.route('/books', methods=['POST'])
def add_book():
    is_authorized, message_to_return = authorize(request.headers)
    if not is_authorized:
        return message_to_return
    

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
    older_data = read_file(DEFAULT_FILE_PATH)
     # Getting older data
    new_book.update({"id": len(older_data)+1})
    older_data.append(new_book)   # attaching new data to older one
    # print(older_data)
    is_updated, message = write_file(file_path=DEFAULT_FILE_PATH, data=older_data)  # writting new data to file/database
    if is_updated:
        return json.dumps(new_book_duplicate), 200  # returning the data that I got as a sign that all check have passed and you data is successfully passed into file/databse
    else:
        return json.dumps({"result": "Fail", "message": f"Something went Wrong! with error: {message}."}), 500  # returning the data that I got as a sign that all check have passed and you data is successfully passed into file/databse
    # return json.dumps({"Hi": 1}), 200

@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    is_authorized, message_to_return = authorize(request.headers)
    if not is_authorized:
        return message_to_return

    books = read_file(DEFAULT_FILE_PATH)
    new_books = []
    for b in books:
        if b["id"] != book_id:
            new_books.append(b)
    write_file(file_path=DEFAULT_FILE_PATH, data=new_books)
    if len(books) != len(new_books):
        return json.dumps({"message" : f"Book by id: {book_id} deleted successfully"}), 200
    else:
        return json.dumps({"message": "No book Found"}), 200

@app.route("/signup", methods =["POST"])
def signup():
    resp = request.data
    try:
        resp_data = json.loads(resp.decode("utf-8"))
    except json.decoder.JSONDecodeError as e:
        return ({"result": "Fail", "message": "Passed Data Format is not JSON"}, 404)
    
    missing_attribute = []
    if not resp_data.get("username", None):
        missing_attribute.append("username")
    if not resp_data.get("password", None):
        missing_attribute.append("password")
    
    if missing_attribute:
        return ({"result": "Fail", "message": f"Required Attributes: {missing_attribute} were not present"}, 404)

    username = resp_data.get("username")
    password = resp_data.get("password")

    # Check if username already exist return "Username already exist" to consumer
    login_data = read_file(file_path="database\\login.json")
    
    if login_data.get("my_data").get(username, None):
        return {"result": "Fail", "message": f"Username: {username} already there! Choose another"}, 200
    
    # If username is not there then update in database and return to consumer
    login_data.get("my_data").update({username: password})
    is_success, any_message = write_file(file_path="database\\login.json", data=login_data)
    
    if is_success:
        return {"result": "Pass", "message": f"Username: {username}, successfully updated"}, 200
    
    return {"result": "Fail", "message": f"Username: {username}, updation Failed"}, 500

    
@app.route("/login", methods=["POST"])
def login():
    resp= request.data
    try:
         resp_data=json.loads(resp.decode("utf-8"))
    except Exception as e:
        return({"result":"fail","message":"data is not json"})
    username=resp_data.get("username")
    password=resp_data.get("password")
    if not username or not password:
        return({"result":"fail","message":"Neither username nor password"})

    logged=read_file(file_path="database\\login.json")

    if logged.get("my_data").get(username)==password:
        token = generate_random()
        token_data = read_file("database\\token.json")
        token_data.get("logged_data").update({token: "True"})
        is_written, message = write_file(file_path="database\\token.json", data=token_data)
        if is_written:
            return ({"result":"Pass","message":"you are logged in.", "token": token}, 200)
        else:
            return ({"result": "Fail", "message": "Server Error"}, 500)
    return({"result":"fail","message":"Invalid Credentials"})

@app.route("/logout", methods=["GET"])
def logout():
    is_authorized, message_to_return = authorize(request.headers)
    if not is_authorized:
        return message_to_return

    token_data: dict = read_file(file_path="database\\token.json")
    user_passed_token = request.headers.get("Authorization")
    deleted_value = token_data.get("logged_data").pop(user_passed_token, None)
    if not deleted_value:
        return {"result" : "Fail", "message": "User not present"}, 404

    is_written, message = write_file(file_path="database\\token.json", data=token_data)
    if not is_written:
        print(f"while deleting token, message: {message}")
        return {"result": "Pass", "message": "Something Went Wrong!"}, 500
    return {"result": "Pass", "message": "Successfully Loged Out!"}



if __name__ == "__main__":
    app.run(debug=True)
