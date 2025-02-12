from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from models import User
from jwt_manager import create_token, validate_token #codifica y decodifica tokens con ciertos contenidos dados
from fastapi.security import HTTPBearer
from dataBase.db import  create_all_tables

from .routers import movies

app = FastAPI(lifespan=create_all_tables)
app.title = "Mi app FastApi"
app.version = "0.0.1"

app.include_router(movies.router)




@app.get("/", tags=["Home"])
def message():
    return HTMLResponse('<h1> Hola mundo </h1>')

@app.post("/Login", tags=['Auth'])
def login(user: User): #genera un token con contenido base del tipo de objeto User
    if user.email == "admin@gmail.com" and user.password == "admin":
        token : str = create_token(user.model_dump()) # "--.model_dump()" se encarga de convertir en un diccionario un 
                                                        #parametro dado como modelo o "BaseModel"
        return JSONResponse(content=token) #con esto ya se ha generado un token


    
    