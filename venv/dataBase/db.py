from typing import Annotated
from fastapi import FastAPI, Depends
from sqlmodel import Session, create_engine, SQLModel

sqlite_name = "db.sqlite3"
sqlite_url = f"sqlite:///C:\\Users\\DEVIN ALZATE\\Documents\\Devin Alzate\\Portafolio\\pythonplatzi\\venv\\dataBase\\{sqlite_name}"

engine = create_engine(sqlite_url) #motor de conexion a una base de datos

def create_all_tables(app : FastAPI):
    SQLModel.metadata.create_all(engine) #Crea todas las tablas en el motor de bases de datos (variable engine)
    yield

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)] #registramos la sesion como 
                                                        #una dependencia de los endpoints