#api.py
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse

from .routers import tx, products, customers
from db.core import get_session, create_db_and_tables   #get_async_session,
  

#from slowapi import Limiter, _rate_limit_exceeded_handler
#from slowapi.errors import RateLimitExceeded
#from slowapi.util import get_remote_address
#limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    #Stuff to do on startup
    create_db_and_tables()
    yield
    #Stuff to do on shutdown
    pass


#-- CRUD app
app = FastAPI(lifespan=lifespan, dependencies=[])


@app.get("/form")
async def get_form():
    return RedirectResponse(url="http://localhost:8501")

app.include_router(customers.router)
app.include_router(products.router)
app.include_router(tx.router)

#app.state.limiter = limiter
#app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
#TODO: investigate why above doesn't work: https://github.com/ArjanCodes/examples/blob/main/2023/fastapi-router/api/main.py


if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=True)
