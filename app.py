from flask import Flask, request
import json
from werkzeug.security import check_password_hash,generate_password_hash
from datetime import timedelta, datetime
from flask_jwt_extended import JWTManager, create_access_token,create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from utilities.common_functions import read_file, write_file

app= Flask(__name__)

app.config["JWT_SECRET_KEY"] = "HIGHLY SECURED KEY"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=30)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days= 30)
jwt= JWTManager(app)
jwt_blocklist = set()

@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payloader):
    jti = jwt_payloader.get("jti")
    return jti in jwt_blocklist

@app.route("/refresh", methods= ["POST"])
@jwt_required(refresh= True)
def refresh():
    username= get_jwt_identity()
    new_token= create_access_token(identity= username)
    return ({"result":"pass","token": new_token})

@app.route("/books", methods = ["GET"])
@jwt_required()
def get_books():
    return (read_file(path = "database\\books.json").get("my_data"), 200)

@app.route("/books/<int:book_id>", methods = ["GET"])
@jwt_required()
def books(book_id):
    books = read_file(path = "database\\books.json")
    for i in books.get("my_data"):
        if i.get("id", -1) == book_id:
            return (json.dumps(i), 200)
    return ({"result": "fail", "message": f"No Book found for id: {book_id}"}, 400)

@app.route("/add_book", methods = ["POST"])
@jwt_required()
def add_book():
   
    # take the data out from request named req
    new = request.data
    try:
    # make it to json to check if it is json req_data
        new_data = json.loads(new.decode("utf-8"))

    except Exception as e:
        return ({"result":"fail","message":"Data is not json"}, 404)

    # Check if missing data in req_data e.g. title, author and cost is there.
    missing_data = []
    # If missing data there then return provide me missing data
    if not new_data.get("title", None):
        missing_data.append("title")
    if not new_data.get("author", None):
        missing_data.append("author")
    if not new_data.get("cost", None):
        missing_data.append("cost")

    if missing_data:
        return ({"result":"fail", "message":f"Data has {missing_data} missing elements"})  
    new_data_duplicate = copy.deepcopy(new_data)
    # read the data from file books named books_data
    book_data = read_file(path ="database\\books.json")
    # prepare your data to be added (req_data) and then add new data to books_data eg. prepare your id field that should be len(books_data) + 1
    new_data.update({"id": len(book_data.get("my_data"))+ 1})
    book_data.get("my_data").append(new_data)

    # write data to database books_data
    is_updated, message = write_file(path ="database\\books.json", data = book_data)

    # if written successfully then return successfully then return req_data
    if is_updated:
        return (json.dumps(new_data_duplicate), 201)
    # if not able to write it to database then return 500 with a message
    return ({"result":"fail", "message":"Something Went Wrong! Please try again!"}, 500)

@app.route("/books/<int:book_id>" , methods = ["DELETE"])
@jwt_required()
def delete_book(book_id):

    # go through data of books
    books = read_file(path="database\\books.json")
    # delete book_id
    new_books = []
    for book in books.get("my_data"):
        if book.get("id") != book_id:
            new_books.append(book)
    #check whether book is there or not
    if len(books.get("my_data")) != len(new_books):
        books.update({"my_data": new_books})
        is_updated, message = write_file(path="database\\books.json", data = books)  
        #if deleted update successfully deleted
        if is_updated:
            return ({"result": "Pass", "message": f"Book with bookid: {book_id} deleted successfully"}, 200)
        #if not then error message
        return ({"result":"fail","message":"Something went wrong"}, 500)

    return ({"result":"fail","message":"book not fond"}, 400)

@app.route("/signup", methods= ["POST"])
def signup():
    req = request.data
    try:
        req_data= json.loads(req.decode("utf-8"))
    except Exception as e:
        return ({"result":"fail", "message":"Data is not json"}, 400)

    username= req_data.get("username")
    password= req_data.get("password")

    if not username or not password:
        return ({"result":"fail", "message":"Neither username nor password"},403)
    logged = read_file(path= "database\\login.json")
    if logged.get("my_data").get("username"):
        return ({"result":"fail", "message":"user already exist"},403)
    hashed_password= generate_password_hash(password)

    logged.get("my_data").update({username:hashed_password})
    is_update,message = write_file(path= "database\\login.json", data =logged)
    if is_update:
        return ({"result":"pass", "message":"You are Logged In"}, 200)
    return ({"result":"fail", "message":"something went wrong"},403)

@app.route("/login",methods=["POST"])
def login():
    resp=request.data
    try:
        resp_data=json.loads(resp.decode("utf-8"))
    except Exception as e:
        return ({"result":"fail","message":"Data is not json"}, 400)
    missing_data=[]
    if not resp_data.get("username",None):
        missing_data.append("username")
    if not resp_data.get("password",None):
        missing_data.append("password",None)
    if missing_data:
        return ({"result": "fail","message": f"Required attributes missing: {missing_data}"}, 403)
    username=resp_data.get("username", None)
    password=resp_data.get("password", None)
    if not username or not password:
        return ({"result":"fail","message":"neither username nor password"}, 400)
        
    logged = read_file(path="database\\login.json")
    stored_hashed_password = logged.get("my_data").get(username)
    if stored_hashed_password and check_password_hash(stored_hashed_password, password):
        token = create_access_token(identity=username)
        refresh_token= create_refresh_token(identity=username)

        return ({"result":"pass", "message":f"{username}!You are Logged In", "token":token, "refresh_token": refresh_token}, 200)
    if not stored_hashed_password:
        return ({"result":"fail", "message":"please signup first"}, 400)
    return ({"result":"fail", "message":"something went wrong"}, 403)

@app.route("/logout", methods= ["DELETE"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    jwt_blocklist.add(jti)
    return ({"result":"pass", "message":"You are successfully logged out"}, 200)

@app.route("/refresh_logout", methods= ["DELETE"])
@jwt_required(refresh=True)
def refresh_logout():
    jti_data = get_jwt()
    jwt_blocklist.add(jti_data["jti"])
    return ({"result":"pass", "message":"You are successfully logged out"}, 200)

if __name__ == "__main__":
    app.run(debug = True)