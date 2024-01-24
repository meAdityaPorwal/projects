from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Annotated
from starlette import status
import models
from models import Todos
from database import SessionLocal
from routers import auth
from .auth import get_current_user

router = APIRouter(
    prefix='/admin',  # dividing the operations according to their file
    tags=['admin']
)

# This will only run when todos.db does not exists
# the above line create everything from our database.py file and models.py file to be created
# a new database that has a new table of 'todos' and all the columns which we have given

# Now, todos.db has been created, so we have to install sqlite on our system

router.include_router(auth.router)


def get_db():
    # create db dependency
    # before each request, we now need to fetch this db session local and be able to open up the
    # connection and close the connection on every request send to this fast api application
    db = SessionLocal()
    try:
        # only the code prior to and including yield statement is executed before sending a response
        # the code following the yield statement, is executed after the response has been delivered.
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/todo", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code= 401, detail= 'Authentication Failed')
    return db.query(Todos).all()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user in None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo Not Found')
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()