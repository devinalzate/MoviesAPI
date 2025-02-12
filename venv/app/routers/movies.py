from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from sqlmodel import select

from jwt_manager import validate_token
from models import Movie, MovieBase
from dataBase.db import SessionDep

router = APIRouter()

class JWTBearer(HTTPBearer): #termina siendo un objeto que enviamos como parametro a una dependecia para que use su funcion __call__ 
                            #para la validacion de tokens y el contenido de estos
    async def __call__(self, request : Request):
        auth = await super().__call__(request) #al ser un parametro que toma un tiempo, se le asigna un parametro await y al mismo tiempo
        #el request es el token que le enviamos                                        # se asigna async a la funcion
        data = validate_token(auth.credentials) #guardamos las credenciales que estaban encriptadas en el token 

        if data['email'] != "admin@gmail.com":
            raise HTTPException(status_code = 403, detail="Credenciales invalidas")


@router.get('/movies', tags=['Movies'], response_model=list[Movie], dependencies=[Depends(JWTBearer())]) #es importante tenerlo como lista
                                                                                                        #todo parametro dado
            #al tener el parametro "dependencies", es necesario contar con el token-validado dado por el 
            # objeto JWTBearer a la hora de querer ejecutar el metodo get, esto debido a que la clase que se esta dando 
            #como dependecia, es una herencia de HTTPBearer 

            #leer especificacion en dependecias.txt. de para que se usa esta clase HTTPBearer
def get_movies(session: SessionDep) -> list[Movie]:
    return session.exec(select(Movie)).all()

@router.get('/movies/{id}', tags=['Movies'], response_model=Movie)
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

@router.get('/moviesByName', tags = ['Movies'], response_model=MovieBase)
def get_movie_by_name(name: str, session: SessionDep) -> MovieBase:
    
    movie = select(Movie).where(Movie.title == name) #con este where deberia de identificar la pelicula con 
                                                    #ese campo pero no esta sucediendo... Arreglo pendiente
    print(movie)
    result = session.exec(movie)
    
    for peli in result:
        return peli

@router.get('/movies/', tags=["Movies"], response_model=list[MovieBase]) 
def get_movie_by_category(session: SessionDep,category_1: str = Query(min_length=5)) -> list[MovieBase]: 
    #aqui le estamos dando un parametro de ruta Query (Cuando solo esta el "/") para 
    #que los valores al ser ingresador no puedan ser invalidos
    
    movieCategory = select(Movie).where(Movie.category == category_1)
    
    resultCategory = session.exec(movieCategory)
    list = []
    for peli in resultCategory:
        list.append(peli.model_dump())
    return list

@router.post('/movies', tags=['Movies'], response_model=Movie)  #Con la especificacion "Body()" decimos que el parametro dado hace parte del cuerpo de la peticion
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

@router.delete('/movies/{id}', tags=['Movies']) #metodo de eliminacion de elementos de un diccionario
def del_movie(id : int, session: SessionDep):
    movieToDelate = session.get(Movie, id)
    if not movieToDelate:
        return JSONResponse(content={"Detail": "movie to delate not found"})
    else:
        session.delete(movieToDelate)
        session.commit()
        return JSONResponse(content={"Detail": "movie delated"})

@router.put('/movies/{id}', tags=['Movies'], response_model=Movie, status_code=status.HTTP_201_CREATED) #metodo de modificacion de elementos de un diccionario
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