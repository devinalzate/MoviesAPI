from sqlmodel import SQLModel , Field, Relationship   #conecta un campo de pydantic con un campo de SQLmodel

class PlanBase(SQLModel):
    name : str = Field(default=None)
    price : int = Field(default=None)
    
    
class Plan(PlanBase, table=True):
    id : int | None = Field(None, primary_key=True)
    movies : list['Movie'] = Relationship(back_populates="plan")

class UserBase(SQLModel):
    email : str
    password: str
    

class User(UserBase, table= True):
    user_name: str | None = Field(None, primary_key=True)
    
class MovieBase(SQLModel): #Esto se hizo con el fin de tener a la clase "Movie" como un esquema, del cual cada que lo
                           # requiramos solo necesitaremos de llamarlo para acceder a atributos de tipo pelicula o "Movie"
    title: str = Field(default=None)             
    overview: str = Field(default=None)               
    year: int = Field(default=None)                  
    rating: float | None = Field(default=None)              
    category: str = Field(default=None)

class Movie(MovieBase, table=True):
    id: int | None = Field(None, primary_key=True)
    plan_id: int | None = Field(foreign_key="plan.id")
    plan: Plan = Relationship(back_populates="movies")

class MovieCreate(MovieBase):
    plan_id: int | None = Field(foreign_key="plan.id")