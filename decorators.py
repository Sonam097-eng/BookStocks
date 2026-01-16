from flask import request
from functools import wraps
from utilities.common_functions import read_file, write_file

def validate_user(f):
    @wraps(f)
    def decorator_function(*args, **kwargs):
        headers = request.headers
        users_token= headers.get("Authorization")
        if not users_token:
            return ({"result": "fail", "message": " user not authorized"}, 403)
        token_value = read_file(path="database\\token.json")
        if token_value.get("logged_data").get(users_token): 
            return f(*args,**kwargs)
        return ({"result":"fail", "message": "User not Authorized"}, 401)

    return decorator_function 