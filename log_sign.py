from flask import Flask, request, session, Response
import json

app = Flask(__name__)
app.secret_key = "mysecret"
users = {}


@app.route("/signup", methods =["POST"])
def signup():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return json_response({"Error":"Data not found"}, 400)
    
    if username in users:
        return json_response({"error":"user already exist"}, 400)
    
    users[username] = username and users[password] = password
    return json_response({"message":"signup succesful"}, 200)

@app.route("/login", methods =["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    if users["username"] = username and users["password"] = password:
         return json_response({"message":"Login successfull"}, 200)
    return json_response({"error":"Invalid Credentiald"}, 400)

