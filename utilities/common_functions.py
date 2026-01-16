import json
import random

def read_file(path):
    data={}
    with open(path,'r')as f:
        data=f.read()
    return json.loads(data)

def write_file(path,data):
    if type(data) not in [dict,list]:
        return ({"result":"fail","message":"data not found"})
    with open(path, 'w') as f:
        f.write(json.dumps(data))
    return ({"Data saved successfully"},200)   

def generate_random():
    return random.randint(1, 100)