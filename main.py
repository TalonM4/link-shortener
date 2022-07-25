from typing import Union
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from deta import Deta
from pydantic import BaseModel
import random
import string

app = FastAPI()

key = open("key.txt", "r")
db = Deta(key.read())
database = db.Base("urls")

class ShortLink(BaseModel):
    key: Union[str, None] = None
    link: str
    num_views: int = 0

@app.get("/")
def read_root():
    return RedirectResponse("https://github.com/talonm4")

@app.get("/exists/{key}")
def return_exists(key: str):
    if database.get(key):
        return True
    else:
        return False

@app.get("/views/{key}")
def return_views(key: str):
    db = database.get(key)
    if db:
        return db["views"]
    else:
        return "This link does not exist"

@app.get("/{key}")
def read_key(key: str):
    db = database.get(key)
    if db:
        db["views"] = int(db["views"]) + 1
        database.put(db)
        return RedirectResponse(db["link"])
    else:
        return "This link does not exist"

@app.post("/shorten")
def create_shortlink(shortlink: ShortLink):
    if shortlink.key:
        database.put({"key": shortlink.key, "link": shortlink.link, "views": 0})
    else:
        counter = 0
        x = "".join(random.choices(string.ascii_letters + string.digits, k=7))
        while database.get(x) and counter != 10:
            x = "".join(random.choices(string.ascii_letters + string.digits, k=7))
            counter += 1
        if counter == 10:
            return "Unable to generate a key within 10 attempts. "
        database.put({"key": x, "link": shortlink.link, "views": 0})
        shortlink.key = x
    return shortlink