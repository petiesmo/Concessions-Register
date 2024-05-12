#api.py
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded


#import api.db.core as db
from api.routers import items #, customers, projects
import api.form
from db.core import get_session
from models import Item, Group
from slowapi import Limiter
from slowapi.util import get_remote_address


limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    #Stuff to do on startup
    db.create_db_and_tables()
    yield
    #Stuff to do on shutdown
    pass

#-- CRUD app
app = FastAPI() #lifespan=lifespan, dependencies=[])

def create_people():
    with get_session() as session:
        first_item = Group(name = 'abc')
        second_item = Item(name = 'efg')


#TODO: App needs to serve the Entry Form webpage
#TODO: App needs to read the returned Form data, and make database calls accordingly

app.include_router(items.router)
#app.include_router(stuff.router)
#app.include_router(projects.router)

app.state.limiter = limiter
#app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
#TODO: investigate why above doesn't work: https://github.com/ArjanCodes/examples/blob/main/2023/fastapi-router/api/main.py

@app.get("/")
#@limiter.limit("1/second")
async def return_html_form():
    basic_screen = "<html><body><h1>The Most Basic HTML ever</h1></body></html>"
    basic_screen = api.form.item_form
    return basic_screen

def main():
    uvicorn.run(app, host='127.0.0.1', port=8005)
    print("running")

if __name__ == '__main__':
    main()