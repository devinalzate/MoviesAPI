from fastapi import APIRouter
from fastapi.responses import JSONResponse
from email_validator import validate_email #validador de correos electronicos

from dataBase.db import SessionDep
from sqlmodel import select
from jwt_manager import create_token
from models import User, UserBase

router = APIRouter()

@router.get("/Get_users", tags=['Users'], response_model=list[User])
def get_users(session: SessionDep) -> list[User]:
    return session.exec(select(User)).all()
    

# @router.post("/Login", tags=['Auth'])
# def login(user: UserBase): #genera un token con contenido base del tipo de objeto User
#     if user.user_name == "Devin" and user.password == "admin":
#         token : str = create_token(user.model_dump()) # "--.model_dump()" se encarga de convertir en un diccionario un 
#                                                         #parametro dado como modelo o "BaseModel"
#         return JSONResponse(content=token) #con esto ya se ha generado un token
    
@router.post("/Create_User", tags=['Users'])
def create_user(session : SessionDep, user:User):
    
    finalUser = UserBase.model_validate(user.model_dump())
    try:
        if validate_email(finalUser.email):
            session.add(finalUser)
            session.commit()
            session.refresh(finalUser)
            return JSONResponse(content={'msg' : "se a creado el usuario de forma correcta"})
    except:   
        return JSONResponse(content={'msg' : "correo electronico falso"})

