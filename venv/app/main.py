from fastapi import FastAPI

from dataBase.db import  create_all_tables

from .routers import movies, users, plans

app = FastAPI(lifespan=create_all_tables)
app.title = "Mi app FastApi"
app.version = "0.0.1"

app.include_router(movies.router)
app.include_router(users.router)
app.include_router(plans.router)




    
    