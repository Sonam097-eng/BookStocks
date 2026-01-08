from flask import Flask, request, session, Response
import json

app = Flask(__name__)
app.secret_key = "mysecret"




@app.route("/signup", methods =["POST"])
def signup():
    # To get data
    resp= request.data
    try:
         resp_data= json.loads(resp.decode("utf-8"))
    except Exception as e:
        return({"result": "Fail","message":"Error has occured"}, 400)
    #reference file
    def read_file(path):
        data=[]
        with open(path, "r")as f:
            data= f.read()
            return json.loads(data)
    def write_file(path,data):
        if type(data)not in [dict,list]:
            return{"result":"fail"}
        with open(path, 'w')as f:
            f.write(json.dumps(data))
        return({"message":"Data saved"})    


    #checked missing data
    missing_data=[]
    if not resp_data.get("username", None):
        missing_data.append("username")
    if not resp_data.get("password", None):
        missing_data.append("password")

    if missing_data:
         return({"result":"Fail","message":"Data not found"}, 400)
    #checking if data matches
    username= resp_data.get("username", None)
    password= resp_data.get("password", None)

    #checking if data is there or not
    logged_data= read_file(path="database\login.json")
    if logged_data.get("my_data").get("username", None):
        return{"result":"fail","message":f"{username}username already exist"}
    
    logged_data.get("my_data").update({username:password})
    isSuccess, message= write_file(path="database\login.json",data=logged_data)

    if isSuccess:
        return{"result":"pass","message":f"{username} username update"}
    return{"result":"fail","message":"updation failed"}

    
if __name__ == "__main__":
    app.run(debug =True)
