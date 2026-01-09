from flask import Flask, request, session, Response,url_for,redirect
import json

app = Flask(__name__)

def get_all_books(file="database\\books.json"):
    data={}
    with open(file,'r')as f:
        data=f.read()
    return json.loads(data)

def read_file(path):
    data={}
    with open(path,'r')as f:
        data= f.read()
    return json.loads(data)
    
def write_file(path,data):
    if type(data) not in [dict,list]:
        return ({"result":"fail","message":"data is not dict"}, 400)
    with open(path,'w')as f:
        f.write(json.dumps(data))
    return ({"data saved successfully"},200)    

@app.route("/books")
def books():
    return(get_all_books)

@app.route("/signup", methods=["POST"])
def signup():
    resp= request.data
    try:
        resp_data=json.loads(resp.decode("utf-8"))
    except Exception as e:
        return ({"result":"fail","message":"data is not json"}, 400)
    
    missing_data=[]
    if not resp_data.get("username", None):
        missing_data.append("username")
    if not resp_data.get("password",None):
        missing_data.append("password")
    if missing_data:
        return ({"result":"fail","message":"missing data"}, 400)
    
    username=resp_data.get("username")
    password=resp_data.get("password")
    if not username or not password:
        return ({"result":"fail", "message":"Neither username nor password"}, 400)

    logged=read_file(path="database\\login.json")

    if logged.get("my_data").get(username, None):
        return ({"message":"user already exist"}, 400)
    
    logged.get("my_data").update({username:password})
    if_its_success, message=write_file(path="database\\login.json",data=logged)
    if if_its_success:
        return ({"result":"pass"}, 200)
    return ({"result":"fail"})

@app.route("/login",methods=["POST"])
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

    logged=read_file(path="database\\login.json")

    if logged.get("my_data").get(username)==password:
        return ({"result":"Pass","message":"you are logged in."})
    return({"result":"fail","message":"Invalid Credentials"})

@app.route("/books_checkout_after_login", methods=["POST"])
def books_checkout_after_login():
    resp= request.data
    try:
         resp_data=json.loads(resp.decode("utf-8"))
    except Exception as e:
        return({"result":"fail","message":"data is not json"})
    username=resp_data.get("username")
    password=resp_data.get("password")
    if not username or not password:
        return({"result":"fail","message":"Neither username nor password"})

    logged=read_file(path="database\\login.json")
    if logged.get("my_data").get(username)==password:
        return redirect(url_for(books))

    



if __name__ == "__main__":
    app.run(debug =True)
