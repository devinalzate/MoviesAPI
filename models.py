from sqlmodel import SQLModel , Field, Relationship, Session, select   #conecta un campo de pydantic con un campo de SQLmodel
from pydantic import field_validator
from dataBase.db import engine
from fastapi import HTTPException , status
    
class MoviesPlan(SQLModel, table = True):
    id : int = Field(primary_key=True)
    movie_id: int = Field(foreign_key="movie.id")
    plan_id: int = Field(foreign_key="plan.id")
    
class PlanBase(SQLModel):
    name : str = Field(default=None)
    price : int = Field(default=None)
    

class Plan(PlanBase, table=True):
    id : int | None = Field(None, primary_key=True)
    users : list['User'] = Relationship(back_populates="plan")
    movies : list['Movie'] = Relationship(
        back_populates="plans", link_model=MoviesPlan
    )

class User(SQLModel, table=True):
    email : str
    password: str
    user_name: str | None = Field(None, primary_key=True)
    plan_id: int | None = Field(foreign_key="plan.id")
    plan: Plan = Relationship(back_populates="users")
    
    @field_validator("email")
    @classmethod
    def validate (cls, value):
        session = Session(engine)
        query = select(User).where(User.email == value)
        result = session.exec(query)
        if result:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="El correo ingresado ya existe")
        return value
   
class MovieBase(SQLModel): #Esto se hizo con el fin de tener a la clase "Movie" como un esquema, del cual cada que lo
                           # requiramos solo necesitaremos de llamarlo para acceder a atributos de tipo pelicula o "Movie"
    title: str = Field(default=None)             
    overview: str = Field(default=None)               
    year: int = Field(default=None)                  
    rating: float | None = Field(default=None)              
    category: str = Field(default=None)

class Movie(MovieBase, table=True):
    id: int | None = Field(None, primary_key=True)
    plans : list[Plan] = Relationship(
        back_populates="movies", link_model=MoviesPlan
    )