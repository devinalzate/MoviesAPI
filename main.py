from fastapi import FastAPI, Body,  Path, Query, status, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from models import User, Movie, MovieBase
from jwt_manager import create_token, validate_token #codifica y decodifica tokens con ciertos contenidos dados
from fastapi.security import HTTPBearer
from db import SessionDep, create_all_tables
from sqlmodel import select

app = FastAPI(lifespan=create_all_tables)
app.title = "Mi app FastApi"
app.version = "0.0.1"

class JWTBearer(HTTPBearer): #termina siendo un objeto que enviamos como parametro a una dependecia para que use su funcion __call__ 
                            #para la validacion de tokens y el contenido de estos
    async def __call__(self, request : Request):
        auth = await super().__call__(request) #al ser un parametro que toma un tiempo, se le asigna un parametro await y al mismo tiempo
        #el request es el token que le enviamos                                        # se asigna async a la funcion
        data = validate_token(auth.credentials) #guardamos las credenciales que estaban encriptadas en el token 

        if data['email'] != "admin@gmail.com":
            raise HTTPException(status_code = 403, detail="Credenciales invalidas")

        

movies = [
    {
        "id": 1,
        "title": "Avatar",
        "overview": "En un exuberante planeta llamado Pandora viven los Na'vi, seres que...",   
        "year": "2019",
        "rating": 7.8,
        "category": "Acción"
    },
    {
        "id": 2,
        "title": "Avatar",
        "overview": "En un exuberante planeta llamado Pandora viven los Na'vi, seres que...",
        "year": "2009",
        "rating": 7.8,
        "category": "Drama"
    }
]

@app.get("/", tags=["Home"])
def message():
    return HTMLResponse('<h1> Hola mundo </h1>')

@app.post("/Login", tags=['Auth'])
def login(user: User): #genera un token con contenido base del tipo de objeto User
    if user.email == "admin@gmail.com" and user.password == "admin":
        token : str = create_token(user.model_dump()) # "--.model_dump()" se encarga de convertir en un diccionario un 
                                                        #parametro dado como modelo o "BaseModel"
        return JSONResponse(content=token) #con esto ya se ha generado un token

@app.get('/movies', tags=['Movies'], response_model=list[Movie], dependencies=[Depends(JWTBearer())]) #es importante tenerlo como lista
                                                                                                        #todo parametro dado
            #al tener el parametro "dependencies", es necesario contar con el token-validado dado por el 
            # objeto JWTBearer a la hora de querer ejecutar el metodo get, esto debido a que la clase que se esta dando 
            #como dependecia, es una herencia de HTTPBearer 

            #leer especificacion en dependecias.txt. de para que se usa esta clase HTTPBearer
def get_movies(session: SessionDep) -> list[Movie]:
    return session.exec(select(Movie)).all()

@app.get('/movies/{id}', tags=['Movies'], response_model=Movie)
def get_movie(session: SessionDep, id: int = Path(ge=1, le=100)) -> Movie | dict: #aqui le estamos dando un parametro de ruta (PATH) para 
                                            #que los valores al ser ingresador no puedan ser invalidos
    movieConsulted = session.get(Movie, id)
    if not movieConsulted:
        return JSONResponse(content={'Detail': "la pelicula no fue encontrada"})
    else:
        return movieConsulted
    
    # for movie in movies:
    #     if movie["id"] == id:
    #         return JSONResponse(content = movie)
    # return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content = {'message' : "No se ha encontrado una pelicula con ese id"})

@app.get('/moviesByName', tags = ['Movies'], response_model=MovieBase)
def get_movie_by_name(title: str) -> MovieBase:
    for item in movies:
        if item['title'] == title:
            return JSONResponse(content = item)
    return JSONResponse(content = {'message' : "No se ha encontrado una pelicula con ese titulo"})


@app.get('/movies/', tags=["Movies"], response_model=list[MovieBase]) 
def get_movie_by_category_year(category: str = Query(min_length=5), year: int = Query(ge=1970, le=2025)) -> list[MovieBase]: 
    #aqui le estamos dando un parametro de ruta Query (Cuando solo esta el "/") para 
    #que los valores al ser ingresador no puedan ser invalidos
    list=[]
    for movie in movies:
        if movie['category'] == category or movie['year'] == str(year):
            list.append(movie)
            
    if list:
        return JSONResponse(content=list)
    else:
        return JSONResponse(content = {'category' : "La categoria no fue encontrada", 'year' : "El año no fue encontrado"})


@app.post('/movies', tags=['Movies'], response_model=Movie)  #Con la especificacion "Body()" decimos que el parametro dado hace parte del cuerpo de la peticion
async def add_movie(movie: MovieBase, session: SessionDep):  #ya no es necesario le "Body()" Debido a que esta definido como esquema o "BaseModel" en la parte superior
    finalMovie = Movie.model_validate(movie.model_dump())
    session.add(finalMovie)
    session.commit()
    session.refresh(finalMovie)
    #asumiendo que movies es en una base de datos
    # finalMovie.id = len(movies) + 1
    # movies.append(finalMovie.model_dump()) # "--.model_dump()" se encarga de convertir en un diccionario un parametro dado como modelo
                                            # o "BaseModel"

    return finalMovie

@app.delete('/movies/{id}', tags=['Movies']) #metodo de eliminacion de elementos de un diccionario
def del_movie(id : int, session: SessionDep):
    movieToDelate = session.get(Movie, id)
    if not movieToDelate:
        return JSONResponse(content={"Detail": "movie to delate not found"})
    else:
        session.delete(movieToDelate)
        session.commit()
        return JSONResponse(content={"Detail": "movie delated"})

@app.put('/movies/{id}', tags=['Movies'], response_model=Movie, status_code=status.HTTP_201_CREATED) #metodo de modificacion de elementos de un diccionario
def change_movie_nameAndYear(id: int, movie: MovieBase, session: SessionDep):
    movieToModify = session.get(Movie, id)
    if movieToModify:
        changes = movie.model_dump(exclude_unset=True) #especifica que se omitiran los datos no rellenados dentro del diccionario
        movieToModify.sqlmodel_update(changes) #se actualzan los campos dados por el diccionario en el campo de la base de datos
        session.add(movieToModify)
        session.commit()
        session.refresh(movieToModify)
        return JSONResponse(content = {'message' : "Se ha modificado correctamente la pelicula"})
    else:
        return JSONResponse(content = {'message' : "No se encontro la pelicula"})
    
    