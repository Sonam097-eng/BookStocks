from flask import Flask, request
import json, copy
from decorators import validate_user
from utilities.common_functions import *


app=Flask(__name__)

@app.route("/books", methods = ["GET"])
@validate_user
def get_books():
    return (read_file(path = "database\\books.json").get("my_data"), 200)

@app.route("/books/<int:book_id>", methods = ["GET"])
@validate_user 
def books(book_id):
    books = read_file(path = "database\\books.json")
    for i in books.get("my_data"):
        if i.get("id", -1) == book_id:
            return (json.dumps(i), 200)
    return ({"result": "fail", "message": f"No Book found for id: {book_id}"}, 400)

@app.route("/add_book", methods = ["POST"])
@validate_user
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
@validate_user
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

@app.route("/signup",methods=["POST"])
def signup():
    req = request.data
    try:
        req_data = json.loads(req)
    except Exception as e:
        return ({"result":"fail", "message": "Data is not json"}, 404)

    username= request.get("username")
    password= request.get("password")
    if not username or not password:
        return ({"result":"fail", "message": "username or password not provided"}, 404)
    
    logged=read_file(path="database\\login.json")
    if logged.get("my_data").get(username,None):
        return ({"result":"fail","message":"user already there"}, 409)
    
    logged.get("my_data").update({username:password})
    is_success, message=write_file(path="database\\login.json",data=logged)
    if is_success:
        return ({"result": "pass","message": "You are Logged In."}, 200)
    return ({"result":"fail","message":"Something went wrong! Please try Again!"}, 500)

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
        
    logged=read_file(path="database\\login.json")
    if logged.get("my_data").get(username) == password:
        # generate token
        token = generate_random()

        # read token file
        token_value = read_file(path="database\\token.json")

        # update token in token_data
        token_value.get("logged_data").update({token: "True"})
        # write updated token_data to file
        is_updated, message = write_file(path="database\\token.json", data=token_value)
            # If success then return 200
        if is_updated:
            return ({"result": "pass","message": "You are Logged In.", "token": token }, 200)
            # if failed then return 500
        return ({"result":"fail","message":"Something went wrong"},500) 

@app.route("/logout",methods= ["DELETE"])
@validate_user
def logout():
    token_data = read_file(path="database\\token.json")
    users_token = request.headers.get("Authorization")
    remove_value = token_data.get("logged_data").pop(users_token)
    if  not remove_value:
        return ({"result":"fail","message":"users_token not found"},200)
    is_written, message = write_file(path= "database\\token.json", data= token_data)
    if is_written:
        return ({"result": "Pass", "message":"logout successfully"})
    
    return ({"result":"fail","message":"Something went wrong"},500)  


if __name__ == "__main__":
    app.run(debug=True)    
