import requests
import json

# resp = requests.get(url="http://127.0.0.1:5000/books")

add_book_url = "http://127.0.0.1:5000/books"
book_to_be_added = {
    "title": "The Ho", 
    "author": "J.",
    "cost": 125
}

resp = requests.post(url=add_book_url, data=json.dumps(book_to_be_added))

print(resp.json())