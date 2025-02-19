from fastapi import APIRouter,status
from fastapi.responses import HTMLResponse, JSONResponse
from sqlmodel import select

from dataBase.db import SessionDep
from models import Plan, PlanBase

router = APIRouter()

@router.get("/plans" , tags=["Plans"])
async def get_plans(session : SessionDep):
    return session.exec(select(Plan)).all()

@router.get("/movies/by/plan", tags=["Plans"])
async def get_movies_of_plan(session : SessionDep, id : int):
    plan = session.get(Plan, id)
    movies : list = plan.movies
    return movies

@router.post("/plans", tags=["Plans"])
async def create_plans(session : SessionDep, plan: PlanBase):
    planFinal = Plan.model_validate(plan.model_dump())
    session.add(planFinal)
    session.commit()
    session.refresh(planFinal)
    
    return JSONResponse(content={'msg' : "el plan ha sido creado con exito"})

