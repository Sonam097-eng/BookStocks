import requests
import json

# resp = requests.get(url="http://127.0.0.1:5000/books")
BASE_URL = "http://127.0.0.1:5000"
url_formed = BASE_URL + "/books/1"
# book_to_be_added = {
#     "title": "The Ho", 
#     "author": "J.",
#     "cost": 125
# }
# resp = requests.post(url=add_book_url, data=json.dumps(book_to_be_added))

headers = {
    "Authorization": "8"
}
resp = requests.get(url=url_formed, headers=headers)
print(resp.json())