from pydantic import BaseModel
from sqlmodel import SQLModel , Field    #conecta un campo de pydantic con un campo de SQLmodel

class User(BaseModel):
    email : str
    password: str

class MovieBase(SQLModel): #Esto se hizo con el fin de tener a la clase "Movie" como un esquema, del cual cada que lo
                           # requiramos solo necesitaremos de llamarlo para acceder a atributos de tipo pelicula o "Movie"
    title: str = Field(default=None)             
    overview: str = Field(default=None)               
    year: int = Field(default=None)                  
    rating: float | None = Field(default=None)              
    category: str = Field(default=None)

class Movie(MovieBase, table=True):
    id: int | None = Field(None, primary_key=True)