#api.py
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded


import app.db.core as db
from app.routers import items #, customers, projects
from app.routers.limiter import limiter

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

app.state.limiter = limiter
#app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
#TODO: investigate why above doesn't work: https://github.com/ArjanCodes/examples/blob/main/2023/fastapi-router/api/main.py


def main():
    pass

if __name__ == '__main__':
    main()