#api.py
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException

import app.db.core as db
from app.routers import items #, customers, projects


@asynccontextmanager
async def lifespan(app: FastAPI):
    #Stuff to do on startup
    db.create_db_and_tables()
    yield
    #Stuff to do on shutdown
    pass

#-- CRUD app
app = FastAPI(lifespan=lifespan, dependencies=[])
#TODO: App needs to serve the Entry Form webpage
#TODO: App needs to read the returned Form data, and make database calls accordingly


app.include_router(items.router)
#app.include_router(stuff.router)
#app.include_router(projects.router)


def main():
    pass

if __name__ == '__main__':
    main()